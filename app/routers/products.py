from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.product import Product, ProductStatus

router = APIRouter(prefix="/products", tags=["products"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_products(
    request: Request,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Product)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    products = query.order_by(Product.name).all()
    return templates.TemplateResponse(
        "products/list.html",
        {"request": request, "current_user": current_user, "products": products, "q": q},
    )


@router.get("/new", response_class=HTMLResponse)
def new_product_form(request: Request, current_user: User = Depends(get_current_user)):
    statuses = [s.value for s in ProductStatus]
    return templates.TemplateResponse(
        "products/form.html",
        {"request": request, "current_user": current_user, "product": None, "statuses": statuses},
    )


@router.post("/")
def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    current_version: Optional[str] = Form(None),
    demo_url: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    docs_url: Optional[str] = Form(None),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = Product(
        name=name,
        description=description,
        current_version=current_version,
        demo_url=demo_url,
        repo_url=repo_url,
        docs_url=docs_url,
        status=ProductStatus(status),
        notes=notes,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return RedirectResponse(url=f"/products/{product.id}", status_code=302)


@router.get("/{product_id}", response_class=HTMLResponse)
def product_detail(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    return templates.TemplateResponse(
        "products/detail.html",
        {"request": request, "current_user": current_user, "product": product},
    )


@router.get("/{product_id}/edit", response_class=HTMLResponse)
def edit_product_form(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    statuses = [s.value for s in ProductStatus]
    return templates.TemplateResponse(
        "products/form.html",
        {"request": request, "current_user": current_user, "product": product, "statuses": statuses},
    )


@router.post("/{product_id}/update")
def update_product(
    product_id: int,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    current_version: Optional[str] = Form(None),
    demo_url: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    docs_url: Optional[str] = Form(None),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    product.name = name
    product.description = description
    product.current_version = current_version
    product.demo_url = demo_url
    product.repo_url = repo_url
    product.docs_url = docs_url
    product.status = ProductStatus(status)
    product.notes = notes
    db.commit()
    return RedirectResponse(url=f"/products/{product_id}", status_code=302)


@router.post("/{product_id}/delete")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse(url="/products", status_code=302)
