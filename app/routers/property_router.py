from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..models import CategoryEnum

router = APIRouter(prefix="/properties", tags=["Properties"])


def _to_out(obj: models.Property) -> schemas.PropertyOut:
    return schemas.PropertyOut.from_orm_obj(obj)


@router.post("", response_model=schemas.PropertyOut, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: schemas.PropertyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    existing = db.query(models.Property).filter(
        models.Property.property_slug == payload.property_slug
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already in use")

    data = payload.model_dump(exclude={"property_image"})
    prop = models.Property(
        **data,
        property_image=",".join(payload.property_image) if payload.property_image else None,
        owner_id=current_user.id,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return _to_out(prop)


@router.get("", response_model=List[schemas.PropertyOut])
def list_properties(
    category: Optional[CategoryEnum] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Public listing - no auth required, so buyers/renters can browse."""
    query = db.query(models.Property).filter(models.Property.status == "active")
    if category:
        query = query.filter(models.Property.category == category)
    props = query.offset(skip).limit(limit).all()
    return [_to_out(p) for p in props]


@router.get("/{property_id}", response_model=schemas.PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return _to_out(prop)


@router.put("/{property_id}", response_model=schemas.PropertyOut)
def update_property(
    property_id: int,
    payload: schemas.PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your property")

    update_data = payload.model_dump(exclude_unset=True)
    if "property_image" in update_data:
        images = update_data.pop("property_image")
        prop.property_image = ",".join(images) if images else None
    for key, value in update_data.items():
        setattr(prop, key, value)

    db.commit()
    db.refresh(prop)
    return _to_out(prop)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your property")

    db.delete(prop)
    db.commit()
    return None
