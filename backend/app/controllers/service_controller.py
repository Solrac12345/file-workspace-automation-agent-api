"""
Service/Automation Rules Controller.
Handles business logic for automation rules (CRUD).
Implements Object-Oriented Programming (OOP) principles.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.service import ServiceCreate, ServiceUpdate, ServiceResponse


class ServiceController:
    """
    Controller class for Service/Automation Rules module.
    Encapsulates database operations and data transformation.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize controller with database connection."""
        self.db = db
        self.collection = db.services  # Colección para las reglas

    def _parse_service(self, doc: dict) -> Optional[ServiceResponse]:
        """Private method to transform MongoDB document to Pydantic model (Encapsulation)."""
        if not doc:
            return None
        
        return ServiceResponse(
            id=str(doc["_id"]),
            name=doc.get("name", "Unknown Rule"),
            description=doc.get("description"),
            file_type=doc.get("file_type", "all"),
            action=doc.get("action", "move"),
            destination=doc.get("destination", "/"),
            is_active=doc.get("is_active", True),
            created_at=doc.get("created_at", datetime.now(timezone.utc)),
            updated_at=doc.get("updated_at"),
        )

    async def create(self, service_data: ServiceCreate) -> ServiceResponse:
        """
        Create a new automation rule.
        """
        now = datetime.now(timezone.utc)
        
        # Convertir Enums a sus valores de string para MongoDB
        service_doc = {
            "name": service_data.name,
            "description": service_data.description,
            "file_type": service_data.file_type.value if hasattr(service_data.file_type, 'value') else service_data.file_type,
            "action": service_data.action.value if hasattr(service_data.action, 'value') else service_data.action,
            "destination": service_data.destination,
            "is_active": service_data.is_active,
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(service_doc)
        service_doc["_id"] = result.inserted_id
        
        return self._parse_service(service_doc)

    async def get_all(self) -> list[ServiceResponse]:
        """Retrieve all automation rules from the database."""
        cursor = self.collection.find({})
        services = []
        async for doc in cursor:
            service = self._parse_service(doc)
            if service:
                services.append(service)
        return services

    async def get_by_id(self, service_id: str) -> Optional[ServiceResponse]:
        """Retrieve a single rule by its MongoDB ID."""
        try:
            oid = ObjectId(service_id)
        except Exception:
            return None
        
        doc = await self.collection.find_one({"_id": oid})
        return self._parse_service(doc)

    async def update(self, service_id: str, service_data: ServiceUpdate) -> Optional[ServiceResponse]:
        """
        Update an existing automation rule.
        Only updates fields that are provided (partial update).
        """
        try:
            oid = ObjectId(service_id)
        except Exception:
            return None

        # Extraer solo los campos que se enviaron
        update_data = service_data.model_dump(exclude_unset=True)
        
        # Manejar conversión de Enums
        if "file_type" in update_data and hasattr(update_data["file_type"], 'value'):
            update_data["file_type"] = update_data["file_type"].value
            
        if "action" in update_data and hasattr(update_data["action"], 'value'):
            update_data["action"] = update_data["action"].value

        update_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            {"_id": oid},
            {"$set": update_data},
            return_document=True
        )
        return self._parse_service(result)

    async def delete(self, service_id: str) -> bool:
        """Delete an automation rule by its MongoDB ID."""
        try:
            oid = ObjectId(service_id)
        except Exception:
            return False
        
        result = await self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0