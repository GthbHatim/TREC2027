from typing import Optional
from app.extensions import db
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

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
    ref_diputacio: Mapped[str] = mapped_column(String(50), unique=True)
    model: Mapped[str] = mapped_column(String(100))
    estat: Mapped[str] = mapped_column(String(20), default="emmagatzemat")
    alumne_id: Mapped[Optional[int]] = mapped_column(ForeignKey("alumne.id"))
    alumne: Mapped[Optional["Alumne"]] = relationship(back_populates="ordinador")


class Historial(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    accio: Mapped[str] = mapped_column(String(50))
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ordinador_id: Mapped[int] = mapped_column(ForeignKey("ordinador.id"))
    alumne_id: Mapped[Optional[int]] = mapped_column(ForeignKey("alumne.id"))