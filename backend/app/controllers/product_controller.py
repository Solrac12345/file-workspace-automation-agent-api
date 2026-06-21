"""
Product/Files Controller.
Handles business logic for workspace file management (CRUD).
Implements Object-Oriented Programming (OOP) principles.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.product import ProductCreate, ProductUpdate, ProductResponse


class ProductController:
    """
    Controller class for Product/Files module.
    Encapsulates database operations and data transformation.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize controller with database connection."""
        self.db = db
        self.collection = db.products  # Colección para los archivos/productos

    def _parse_product(self, doc: dict) -> Optional[ProductResponse]:
        """Private method to transform MongoDB document to Pydantic model (Encapsulation)."""
        if not doc:
            return None
        
        return ProductResponse(
            id=str(doc["_id"]),
            name=doc.get("name", "Unknown File"),
            category=doc.get("category", "other"),
            file_path=doc.get("file_path", "/"),
            file_size=doc.get("file_size", 0),
            mime_type=doc.get("mime_type", "application/octet-stream"),
            description=doc.get("description"),
            tags=doc.get("tags", []),
            is_archived=doc.get("is_archived", False),
            owner_id=doc.get("owner_id"),
            created_at=doc.get("created_at", datetime.now(timezone.utc)),
            updated_at=doc.get("updated_at"),
        )

    async def create(self, product_data: ProductCreate) -> ProductResponse:
        """
        Create a new file record.
        """
        now = datetime.now(timezone.utc)
        
        # Convertir Enums a sus valores de string para MongoDB
        product_doc = {
            "name": product_data.name,
            "category": product_data.category.value if hasattr(product_data.category, 'value') else product_data.category,
            "file_path": product_data.file_path,
            "file_size": product_data.file_size,
            "mime_type": product_data.mime_type,
            "description": product_data.description,
            "tags": product_data.tags,
            "is_archived": product_data.is_archived,
            "owner_id": product_data.owner_id,
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(product_doc)
        product_doc["_id"] = result.inserted_id
        
        return self._parse_product(product_doc)

    async def get_all(self) -> list[ProductResponse]:
        """Retrieve all file records from the database."""
        cursor = self.collection.find({})
        products = []
        async for doc in cursor:
            product = self._parse_product(doc)
            if product:
                products.append(product)
        return products

    async def get_by_id(self, product_id: str) -> Optional[ProductResponse]:
        """Retrieve a single file record by its MongoDB ID."""
        try:
            oid = ObjectId(product_id)
        except Exception:
            return None
        
        doc = await self.collection.find_one({"_id": oid})
        return self._parse_product(doc)

    async def update(self, product_id: str, product_data: ProductUpdate) -> Optional[ProductResponse]:
        """
        Update an existing file record.
        Only updates fields that are provided (partial update).
        """
        try:
            oid = ObjectId(product_id)
        except Exception:
            return None

        # Extraer solo los campos que se enviaron
        update_data = product_data.model_dump(exclude_unset=True)
        
        # Manejar conversión de Enums
        if "category" in update_data and hasattr(update_data["category"], 'value'):
            update_data["category"] = update_data["category"].value

        update_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            {"_id": oid},
            {"$set": update_data},
            return_document=True
        )
        return self._parse_product(result)

    async def delete(self, product_id: str) -> bool:
        """Delete a file record by its MongoDB ID."""
        try:
            oid = ObjectId(product_id)
        except Exception:
            return False
        
        result = await self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0