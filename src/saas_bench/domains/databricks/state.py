"""Databricks state schema using Pydantic models."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Column(BaseModel):
    """Represents a table column."""

    name: str
    type: str  # e.g., "INT", "STRING", "DOUBLE"
    nullable: bool = True
    comment: Optional[str] = None

    model_config = {"frozen": True}


class Catalog(BaseModel):
    """Unity Catalog catalog."""

    name: str
    owner: str
    comment: Optional[str] = None
    properties: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True}


class Schema(BaseModel):
    """Unity Catalog schema."""

    catalog_name: str
    schema_name: str
    owner: str
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True}


class Table(BaseModel):
    """Unity Catalog table."""

    catalog_name: str
    schema_name: str
    table_name: str
    columns: List[Column]
    data: List[Dict] = Field(default_factory=list)  # Table rows as dicts
    owner: str
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True}


class Notebook(BaseModel):
    """Databricks notebook."""

    path: str
    language: str  # "sql", "python", "scala", "r"
    cells: List[str] = Field(default_factory=list)
    attached_cluster_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True}


class Cluster(BaseModel):
    """Compute cluster."""

    cluster_id: str
    name: str
    state: str  # "RUNNING", "TERMINATED", "PENDING", etc.
    node_type: str
    num_workers: int
    spark_version: str
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True}


class Job(BaseModel):
    """Scheduled job."""

    job_id: str
    name: str
    schedule: Optional[str] = None  # Cron expression
    tasks: List[Dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True}


class Permission(BaseModel):
    """Access control permission."""

    principal: str  # User or group name
    privilege: str  # "SELECT", "INSERT", "MODIFY", "ALL_PRIVILEGES", etc.
    securable_type: str  # "TABLE", "CATALOG", "SCHEMA", etc.
    securable_name: str  # e.g., "catalog.schema.table"

    model_config = {"frozen": True}


class DatabricksState(BaseModel):
    """Root state container for Databricks workspace."""

    catalogs: Dict[str, Catalog] = Field(default_factory=dict)
    schemas: Dict[str, Schema] = Field(default_factory=dict)  # Key: "catalog.schema"
    tables: Dict[str, Table] = Field(
        default_factory=dict
    )  # Key: "catalog.schema.table"
    notebooks: Dict[str, Notebook] = Field(default_factory=dict)  # Key: notebook path
    clusters: Dict[str, Cluster] = Field(default_factory=dict)  # Key: cluster_id
    jobs: Dict[str, Job] = Field(default_factory=dict)  # Key: job_id
    permissions: List[Permission] = Field(default_factory=list)
    active_catalog: Optional[str] = None  # Current catalog context

    model_config = {"frozen": True}

    def get_schema_key(self, catalog_name: str, schema_name: str) -> str:
        """Get the key for a schema in the schemas dict."""
        return f"{catalog_name}.{schema_name}"

    def get_table_key(
        self, catalog_name: str, schema_name: str, table_name: str
    ) -> str:
        """Get the key for a table in the tables dict."""
        return f"{catalog_name}.{schema_name}.{table_name}"
