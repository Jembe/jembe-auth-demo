from typing import TYPE_CHECKING, Optional, Union, Iterable, Dict, Callable, Tuple
import sqlalchemy as sa
from sqlalchemy.orm.attributes import QueryableAttribute
from jembe import Component, config

if TYPE_CHECKING:
    from flask import Response
    from flask_sqlalchemy import SQLAlchemy
    from jembe import ComponentConfig, ComponentRef, RedisplayFlag

__all__ = ("CTable", "TableColumn")


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
                    self.query_attribute.name
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
        return self.get_value(record)


# TODO aplly this params event if config exists
# @config(Component.Config(url_query_params=dict(o="order_by")))
class CTable(Component):
    class Config(Component.Config):
        def __init__(
            self,
            db: "SQLAlchemy",
            query: sa.orm.Query,
            columns: Iterable["TableColumn"],
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = dict(o="order_by"),
        ):
            self.db = db
            self.query = query
            self.columns = [c.mount(self.query) for c in columns]

            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

    _config: Config

    def __init__(self, order_by: int = 0):
        super().__init__()

    # TODO
    # order them
    # filter them
    # paginate them
    # select them
    # execute action on them
    def display(self) -> Union[str, "Response"]:
        query = self._config.query.with_session(self._config.db.session())
        if self.state.order_by != 0:
            ob = self._config.columns[abs(self.state.order_by) - 1].query_attribute
            ob = ob if self.state.order_by > 0 else ob.desc()
            query = query.order_by(ob)
        self.data = query[:10]
        return super().display()
