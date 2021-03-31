from typing import TYPE_CHECKING, Optional, Union, Iterable, Dict, Callable, Tuple, List
from math import ceil
import sqlalchemy as sa
from sqlalchemy.orm.attributes import QueryableAttribute
from jembe import Component, listener
from jembe_auth_demo.pages.common import Link, Menu
from .create import CCreate

if TYPE_CHECKING:
    from jembe import Event
    from flask import Response
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.sql.elements import ColumnElement
    from jembe import ComponentConfig, ComponentRef, RedisplayFlag

__all__ = ("CTable", "CCrudTable", "TableColumn")


class TableColumn:
    def __init__(
        self,
        query_attribute: Union[QueryableAttribute, str],
        title: Optional[str] = None,
    ) -> None:
        self.query_attribute = query_attribute
        self.title = title
        self._query: Optional[sa.orm.Query] = None

    def mount(self, query: sa.orm.Query) -> "TableColumn":
        self._query = query
        if self.title is None:
            if isinstance(self.query_attribute, QueryableAttribute):
                # exm: Group.id
                self.title = (
                    " ".join(self.query_attribute.name.split("_")).title()
                    if not self.query_attribute.info.get("verbose_name", None)
                    else self.query_attribute.info["verbose_name"]
                )
            else:
                raise NotImplementedError()

        return self

    def get_value(self, record):
        try:
            # exm: query(Group), Group.id
            return getattr(record, self.query_attribute.name)
        except AttributeError:
            return getattr(
                getattr(record, self.query_attribute.class_.__name__),
                self.query_attribute.name,
            )

    def render_value(self, record) -> str:
        value = self.get_value(record)
        return value if value is not None else ""


# TODO aplly this params event if config exists
# @config(Component.Config(url_query_params=dict(o="order_by")))
class CTable(Component):
    class Config(Component.Config):
        def __init__(
            self,
            db: "SQLAlchemy",
            query: sa.orm.Query,
            columns: Iterable["TableColumn"],
            default_filter: Optional[Callable[[str], "ColumnElement"]] = None,
            title: Optional[str] = None,
            top_menu: Optional[Union[List[Union["Link", "Menu"]], "Menu"]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            self.title = title
            self.db = db
            self.query = query
            self.columns = [c.mount(self.query) for c in columns]

            if url_query_params is None:
                url_query_params = dict()
            if "order_by" not in url_query_params.values():
                url_query_params["o"] = "order_by"
            if "page" not in url_query_params.values():
                url_query_params["p"] = "page"
            if "page_size" not in url_query_params.values():
                url_query_params["ps"] = "page_size"
            if "search_query" not in url_query_params.values():
                url_query_params["q"] = "search_query"

            self.default_filter = default_filter

            self.default_template = "common/table.html"
            if template is None:
                template = ("", self.default_template)

            self.top_menu: "Menu" = (
                Menu()
                if top_menu is None
                else (Menu(top_menu) if not isinstance(top_menu, Menu) else top_menu)
            )

            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

    _config: Config

    def __init__(
        self,
        order_by: int = 0,
        page: int = 0,
        page_size: int = 10,
        search_query: Optional[str] = None,
    ):
        if page_size <= 0:
            self.state.page_size = 10
        super().__init__()

    # TODO
    # advance filters
    # select them
    # execute action on them
    def display(self) -> Union[str, "Response"]:
        query = self._config.query.with_session(self._config.db.session())
        # order
        if self.state.order_by != 0:
            ob = self._config.columns[abs(self.state.order_by) - 1].query_attribute
            ob = ob if self.state.order_by > 0 else ob.desc()
            query = query.order_by(None).order_by(ob)

        # default filter
        if self._config.default_filter is not None and self.state.search_query:
            filter = sa.sql.true()
            for word in self.state.search_query.split():
                if word:
                    filter = filter & self._config.default_filter(word)
            query = query.filter(filter)

        # paginate
        self.total_records = query.count()
        self.total_pages = ceil(self.total_records / self.state.page_size)
        if self.state.page > self.total_pages - 1:
            self.state.page = self.total_pages - 1
        if self.state.page < 0:
            self.state.page = 0
        self.start_record_index = self.state.page * self.state.page_size
        self.end_record_index = self.start_record_index + self.state.page_size
        if self.end_record_index > self.total_records:
            self.end_record_index = self.total_records
        self.data = query[self.start_record_index : self.end_record_index]

        # initialise menues
        self.top_menu = self._config.top_menu.bind_to(self)

        return super().display()


class CCrudTable(CTable):
    """
    Table that support create, read, update, delete subcomponents
    displayed instead of table
    """
    class Config(CTable.Config):
        def __init__(
            self,
            db: "SQLAlchemy",
            query: sa.orm.Query,
            columns: Iterable["TableColumn"],
            default_filter: Optional[Callable[[str], "ColumnElement"]] = None,
            title: Optional[str] = None,
            top_menu: Optional[Union[List[Union["Link", "Menu"]], "Menu"]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            super().__init__(
                db,
                query,
                columns,
                default_filter=default_filter,
                title=title,
                top_menu=top_menu,
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )
            self.supported_display_modes = [
                cname
                for cname, cclass in self.components_classes.items()
                if issubclass(cclass, (CCreate,))
            ]

    _config: Config

    def __init__(
        self,
        order_by: int = 0,
        page: int = 0,
        page_size: int = 10,
        search_query: Optional[str] = None,
        display_mode: Optional[str] = None,
    ):
        if display_mode is not None and (
            display_mode not in self._config.supported_display_modes
            or display_mode.startswith("_")
        ):
            self.state.display_mode = None

        super().__init__(
            order_by=order_by, page=page, page_size=page_size, search_query=search_query
        )

    @listener(event="_display", source="./*")
    def on_child_display(self, event: "Event"):
        if event.source_name in self._config.supported_display_modes:
            self.state.display_mode = event.source_name

    @listener(event=["save", "cancel"], source="./*")
    def on_child_finish(self, event: "Event"):
        if event.source_name in self._config.supported_display_modes:
            self.state.display_mode = None
