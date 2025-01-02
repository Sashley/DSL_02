from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class FieldDef(BaseModel):
    type: str
    primary_key: Optional[bool] = False
    nullable: Optional[bool] = True
    default: Optional[str] = None
    unique: Optional[bool] = False
    foreign_key: Optional[str] = None
    auto_increment: Optional[bool] = False


class MenuContext(BaseModel):
    drill_down: Optional[str] = None
    related_table: Optional[str] = None
    route: str


class Menu(BaseModel):
    Main: List[Dict[str, str]]
    Context: Optional[Dict[str, List[MenuContext]]] = {}
    Statistics: Optional[Dict[str, List[str]]] = {}


class Model(BaseModel):
    Fields: Dict[str, FieldDef]
    Indices: Optional[Dict[str, List[str]]] = {}
    Menus: Optional[Dict[str, List[MenuContext]]] = {}


class DSLValidation(BaseModel):
    version: str
    Models: Dict[str, Model]
    Menus: Menu
