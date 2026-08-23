from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class RawProductInput(BaseModel):
    mfg_part_num: Optional[str] = None
    part_desc: Optional[str] = None
    e1_brand: Optional[str] = None
    unilog_brand: Optional[str] = None
    dib_brand: Optional[str] = None
    part_manuf: Optional[str] = None

class CleanedField(BaseModel):
    original_value: Optional[str] = None
    normalized_value: Optional[str] = None

class CleanedProductInput(BaseModel):
    mfg_part_num: CleanedField = Field(default_factory=CleanedField)
    part_desc: CleanedField = Field(default_factory=CleanedField)
    e1_brand: CleanedField = Field(default_factory=CleanedField)
    unilog_brand: CleanedField = Field(default_factory=CleanedField)
    dib_brand: CleanedField = Field(default_factory=CleanedField)
    part_manuf: CleanedField = Field(default_factory=CleanedField)

class IdentityEvidence(BaseModel):
    field: str
    value: Optional[str] = None
    source: str
    evidence: str
    status: str

class ProductIdentity(BaseModel):
    raw_mpn: Optional[str] = None
    normalized_mpn: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacturer_candidates: List[str] = Field(default_factory=list)
    brand: Optional[str] = None
    brand_candidates: List[str] = Field(default_factory=list)
    product_name: Optional[str] = None
    alternate_mpn: Optional[str] = None
    identity_confidence: float = 0.0
    identity_status: str = "UNKNOWN"  # VERIFIED, PROBABLE, AMBIGUOUS, UNKNOWN, CONFLICTED
    identity_evidence: List[IdentityEvidence] = Field(default_factory=list)

class ProductTaxonomy(BaseModel):
    department: Optional[str] = None
    class_name: Optional[str] = Field(None, alias="class")
    fine: Optional[str] = None
    classpath: Optional[str] = None
    product_type: Optional[str] = None
    product_family: Optional[str] = None
    confidence: float = 0.0
    status: str = "UNKNOWN"
    method: str = "unknown"
    evidence: Optional[str] = None
    unspsc: Optional[str] = None

class ProductAttribute(BaseModel):
    label: str
    value: Any
    raw_value: Optional[Any] = None
    uom: Optional[str] = None
    normalized_value: Optional[Any] = None
    status: str = "UNKNOWN"
    confidence: float = 0.0
    source: Optional[str] = None
    evidence: Optional[str] = None

class ProductSource(BaseModel):
    url: str
    domain: str
    source_type: str
    authority_level: str
    title: Optional[str] = None
    description: Optional[str] = None
    retrieved_at: Optional[str] = None
    content_hash: Optional[str] = None
    http_status: Optional[int] = None
    extraction_status: Optional[str] = None
    relevance_score: float = 0.0
    authority_score: float = 0.0
    final_score: float = 0.0
    source_origin: str = "LIVE"

class ProductContent(BaseModel):
    product_title: Optional[str] = None
    short_desc: Optional[str] = None
    long_desc: Optional[str] = None
    invoice_desc: Optional[str] = None
    mobile_desc: Optional[str] = None

class ProductValidation(BaseModel):
    schema_compliant: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    quality_state: str = "UNKNOWN"

class CanonicalProduct(BaseModel):
    raw: RawProductInput = Field(default_factory=RawProductInput)
    cleaned: CleanedProductInput = Field(default_factory=CleanedProductInput)
    identity: ProductIdentity = Field(default_factory=ProductIdentity)
    taxonomy: ProductTaxonomy = Field(default_factory=ProductTaxonomy)
    attributes: List[ProductAttribute] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    content: ProductContent = Field(default_factory=ProductContent)
    sources: List[ProductSource] = Field(default_factory=list)
    assets: List[str] = Field(default_factory=list)
    validation: ProductValidation = Field(default_factory=ProductValidation)
    enriched_attributes: List[ProductAttribute] = Field(default_factory=list)
    source_conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    web_quality_score: float = 0.0
