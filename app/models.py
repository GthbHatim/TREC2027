from typing import Optional
from app.extensions import db
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

ESTATS_ORDINADOR = {
    "assignat": "Assignat",
    "emmagatzemat": "Al magatzem",
    "reparacio": "En reparació",
    "de baixa": "De baixa",
}

ACCIONS_HISTORIAL = {
    "assignat": "Assignat",
    "retirat": "Retirat",
    "retirat (emmagatzemat)": "Retirat",
    "retirat (reparació)": "Retirat per reparar",
    "retirat (baixa)": "Retirat per baixa de l'equip",
    "retirat (baixa alumne)": "Retirat per baixa de l'alumne",
    "reparacio": "Enviat a reparació",
    "de baixa": "Donat de baixa",
    "emmagatzemat": "Emmagatzemat",
    "emmagatzemat (reparació)": "Emmagatzemat després de reparació",
    "restaurat": "Restaurat al magatzem",
}

CURSOS = ["1r ESO", "2n ESO", "3r ESO", "4t ESO", "1r Batx", "2n Batx"]


class Alumne(db.Model):
    nom: Mapped[str] = mapped_column(String(50), unique=True)
    id: Mapped[int] = mapped_column(primary_key=True)
    identificador: Mapped[str] = mapped_column(String(50), unique=True)
    curs: Mapped[str] = mapped_column(String(50))
    ordinador: Mapped[Optional["Ordinador"]] = relationship(back_populates="alumne")
    estat: Mapped[str] = mapped_column(String(50), default="actiu")
    email: Mapped[str] = mapped_column(String(50), unique=True)


class Ordinador(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    num_serie: Mapped[str] = mapped_column(String(50), unique=True)
    sace: Mapped[str] = mapped_column(String(50), unique=True)
    model: Mapped[str] = mapped_column(String(100))
    estat: Mapped[str] = mapped_column(String(20), default="emmagatzemat")
    alumne_id: Mapped[Optional[int]] = mapped_column(ForeignKey("alumne.id"))
    alumne: Mapped[Optional["Alumne"]] = relationship(back_populates="ordinador")


class Historial(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    accio: Mapped[str] = mapped_column(String(50))
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    ordinador_id: Mapped[int] = mapped_column(ForeignKey("ordinador.id"))          
    alumne_id: Mapped[Optional[int]] = mapped_column(ForeignKey("alumne.id"))      
    ordinador: Mapped["Ordinador"] = relationship()                              
    alumne: Mapped[Optional["Alumne"]] = relationship()                          