"""Pydantic models for request/response schemas."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Response timestamp")
    version: str = Field(..., description="Application version")
    message: str | None = Field(default=None, description="Additional status message")
    database: dict[str, Any] | None = Field(default=None, description="Database status")
    ai_service: dict[str, Any] | None = Field(
        default=None, description="AI service status"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type")
    detail: str | None = Field(default=None, description="Error details")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )


class RootResponse(BaseModel):
    """Root endpoint response model."""

    message: str = Field(..., description="Welcome message")
    version: str = Field(..., description="Application version")
    docs: str = Field(..., description="Documentation URL")
    health: str = Field(..., description="Health check URL")


# --- Biotasys Specific Schemas ---


class SequencingData(BaseModel):
    """Technical sequencing and quality metadata."""

    technology: str = Field(default="No disponible")
    region: str = Field(default="No disponible")
    platform: str = Field(default="No disponible")
    total_reads: int = Field(default=0)
    filtered_reads: int = Field(default=0)


class DiversityIndices(BaseModel):
    """Ecological diversity and richness metrics."""

    shannon_index: float = Field(default=0.0)
    simpson_index: float = Field(default=0.0)
    observed_otus: int = Field(default=0)


class TaxonomicAbundance(BaseModel):
    """Relative abundance of a taxonomic unit."""

    name: str = Field(..., description="Name of the taxon")
    abundance: float = Field(..., description="Relative abundance percentage")


class TaxonomicComposition(BaseModel):
    """Distribution of bacteria across different levels."""

    phyla: list[TaxonomicAbundance] = Field(default_factory=list)
    firmicutes_bacteroidetes_ratio: float = Field(default=0.0)
    predominant_genera: list[TaxonomicAbundance] = Field(default_factory=list)
    detected_species: list[TaxonomicAbundance] = Field(default_factory=list)
    other_phyla_abundance: float = Field(
        default=0.0,
        description="Cumulative abundance of all other phyla not explicitly listed",
    )

    @model_validator(mode="after")
    def calculate_fb_ratio(self) -> "TaxonomicComposition":
        """Fail-safe: Calculate ratio if missing but phyla data is present."""
        if self.firmicutes_bacteroidetes_ratio > 0:
            return self

        f_abun = next(
            (p.abundance for p in self.phyla if p.name.lower() == "firmicutes"), 0.0
        )
        b_abun = next(
            (p.abundance for p in self.phyla if p.name.lower() == "bacteroidetes"), 0.0
        )

        if b_abun > 0:
            self.firmicutes_bacteroidetes_ratio = round(f_abun / b_abun, 2)

        return self


class OpportunisticPathogen(BaseModel):
    """Status of a specific opportunistic microorganism."""

    genus: str = Field(..., description="Genus name")
    species: str = Field(default="spp.")
    status: str = Field(default="No detectado")
    note: str | None = None


class FunctionalMarkerItem(BaseModel):
    """Evaluation of a specific functional pathway or gene."""

    marker_name: str
    status: str = Field(default="Normal")
    value: str | None = None


class FunctionalMarkers(BaseModel):
    """Functional and microbiological markers."""

    butyrate_producers: str = Field(default="No disponible")
    propionate_producers: str = Field(default="No disponible")
    suggested_enterotype: str = Field(default="No disponible")
    opportunistic_microorganisms: list[OpportunisticPathogen] = Field(
        default_factory=list
    )
    functional_markers_list: list[FunctionalMarkerItem] = Field(default_factory=list)
    # PICRUSt Functional Genes
    carbohydrate_metabolism: str = Field(
        default="No disponible",
        description="Inferred metabolic level for Carbohydrates",
    )
    lipid_metabolism: str = Field(
        default="No disponible", description="Inferred metabolic level for Lipids"
    )
    vitamin_b_synthesis: str = Field(
        default="No disponible",
        description="Inferred level for Vitamin B Group synthesis",
    )


class StudyMetadata(BaseModel):
    """Administrative and demographic metadata."""

    study_code: str = Field(default="No disponible")
    lab_internal_code: str = Field(default="No disponible")
    patient_id: str = Field(default="No disponible")
    sex: str = Field(default="No disponible")
    age: int = Field(default=0)
    sample_collection_date: datetime | None = None
    sample_reception_date: datetime | None = None
    sample_type: str = Field(default="Materia fecal")
    sample_collection_method: str = Field(default="No disponible")
    transport_conditions: str = Field(default="No disponible")
    sample_status: str = Field(default="No disponible")


class ClinicalContext(BaseModel):
    """Clinical history and observations."""

    inflammatory_markers: str = Field(default="No disponible")
    antibiotic_use: bool = Field(default=False)
    probiotic_use: bool = Field(default=False)
    dietary_pattern: str = Field(default="No disponible")
    lab_observations: str = Field(default="No disponible")


class ClinicalObservation(BaseModel):
    """A technical observation or alert."""

    title: str
    severity: str
    description: str


class GutHealthScore(BaseModel):
    """Overall gut health assessment."""

    value: float = Field(..., description="Global health score from 0 to 100")
    label: str = Field(
        ..., description="Qualitative label (e.g. 'Excelente', 'Necesita Mejorar')"
    )
    breakdown: str = Field(
        ..., description="Explanation of how the score was calculated"
    )


class DietaryRecommendation(BaseModel):
    """Specific dietary advice based on microbiota analysis."""

    item: str = Field(..., description="Food item or nutrient")
    action: str = Field(
        ..., description="Action to take: 'Aumentar', 'Reducir', 'Evitar'"
    )
    reason: str = Field(
        ..., description="Why this recommendation is made based on microbiota"
    )


class SupplementSuggestion(BaseModel):
    """Supplement recommendation."""

    type: str = Field(..., description="Type: 'Probiótico', 'Prebiótico', 'Suplemento'")
    name: str = Field(
        ..., description="Specific name (e.g. 'Lactobacillus rhamnosus GG')"
    )
    reason: str = Field(..., description="Targeted benefit")


class FunctionalInterpretation(BaseModel):
    """Interpretation of metabolic pathways."""

    pathway: str
    status: str
    note: str


class DiversityDiagnosis(BaseModel):
    """Structured interpretation of diversity metrics."""

    score: float = Field(
        ..., description="The calculated diversity score (e.g. Shannon)"
    )
    interpretation: str = Field(
        ..., description="Qualitative assessment (e.g. 'High', 'Low', 'Optimal')"
    )
    clinical_implication: str = Field(
        ..., description="What this means for the patient"
    )


class MetabolicFunction(BaseModel):
    """Inferred metabolic capability based on bacterial abundance."""

    pathway: str = Field(
        ..., description="Metabolic pathway (e.g. 'Butyrate Production')"
    )
    status: str = Field(
        ..., description="Activity level (e.g. 'Reduced', 'Normal', 'Enhanced')"
    )
    associated_bacteria: list[str] = Field(
        default_factory=list, description="Bacteria driving this finding"
    )
    implication: str = Field(..., description="Biological consequence")


class EnterotypeClassification(BaseModel):
    """Enterotype classification based on dominant genera."""

    enterotype: str = Field(..., description="Primary enterotype (e.g. 'Bacteroides')")
    confidence: str = Field(
        default="Medium", description="Confidence level of classification"
    )
    description: str = Field(..., description="Characteristics of this enterotype")

class LuisMicrobiotaInterpretation(BaseModel):
    """Esquema de análisis clínico de los datos microbiota realizado por la IA"""

    summary: str = Field(..., description="Executive summary of the microbiota status")
    gut_health_score: GutHealthScore
    diversity_diagnosis: DiversityDiagnosis
    enterotype_analysis: EnterotypeClassification
    taxonomic_balance: list[ClinicalObservation] = Field(default_factory=list)
    metabolic_potential: list[MetabolicFunction] = Field(default_factory=list)
    opportunistic_risk: list[ClinicalObservation] = Field(default_factory=list)
    dietary_recommendations: list[DietaryRecommendation] = Field(default_factory=list)
    supplement_suggestions: list[SupplementSuggestion] = Field(default_factory=list)
    final_technical_notes: str 

class MicrobiotaReport(BaseModel):
    """Full structured microbiota report."""

    metadata: StudyMetadata = Field(default_factory=StudyMetadata)
    sequencing: SequencingData = Field(default_factory=SequencingData)
    diversity: DiversityIndices = Field(default_factory=DiversityIndices)
    taxonomy: TaxonomicComposition = Field(default_factory=TaxonomicComposition)
    functionality: FunctionalMarkers = Field(default_factory=FunctionalMarkers)
    clinical_context: ClinicalContext = Field(default_factory=ClinicalContext)
    interpretation: LuisMicrobiotaInterpretation | None = None
    engine_version: str = Field(default="1.2.5")
    processed_at: datetime = Field(default_factory=datetime.now)

class AnalysisRequest(BaseModel):
    """Payload requirement from Backend A to Backend B."""

    file_url: str
    documento_id: str
    empresa_id: str
    doctor_id: str
    fecha_envio: datetime

""" class PatientInfo(BaseModel):
    Información básica del paciente.

    id: str = Field(..., description="Patient ID associated with the report")
    sex: str = Field(..., description="Patient sex")
    age: int = Field(..., description="Patient age")  """

""" class NutricionistInfo(BaseModel):
    Información del nutricionista.

    id: int = Field(..., description="Nutritionist ID associated with the report")
    name: str = Field(..., description="Nutritionist name associated with the report") """

class JsonAnalysisRequest(BaseModel):
    """Esquema de petición de análisis de Backend Nest"""

    study_id: str = Field(..., description="Unique identifier for the study")
    study_code: str = Field(..., description="Study code associated with the report")
    nutricionist_id: str = Field(..., description="Nutritionist information for validation and association")
    patient_id: str = Field(..., description="Patient associated with the report")
    raw_json: dict[str, Any] = Field(..., description="Raw JSON input from Backend Nest for analysis")
    study_date: datetime = Field(..., description="Date when the study was created")

class MicrobiotaInput(BaseModel):
    """Esquema normalizado de los datos de microbiota"""

    metadata: StudyMetadata = Field(default_factory=StudyMetadata)
    sequencing: SequencingData = Field(default_factory=SequencingData)
    diversity: DiversityIndices = Field(default_factory=DiversityIndices)
    taxonomy: TaxonomicComposition = Field(default_factory=TaxonomicComposition)
    functionality: FunctionalMarkers = Field(default_factory=FunctionalMarkers)
    clinical_context: ClinicalContext = Field(default_factory=ClinicalContext)

class GeneralSummary(BaseModel):
    """Final technical observations and conclusions based on the microbiota analysis."""

    summary: str = Field(
        ..., description="Summary of the final conclusions based on the microbiota status"
    )
    summary_tags: list[str] = Field(
        default_factory=list, description="Short tags summarizing the overall microbiota status (e.g. 'Dysbiosis', 'Optimal Diversity')"
    )
    firmicutes_bacteroidetes_ratio: float = Field(
        default=0.0, description="Calculated Firmicutes/Bacteroidetes ratio"
    )
    firmicutes_bacteroidetes_range: str = Field(
        default="", description="Clinical range for F/B ratio (e.g. 'High', 'Low')"
    )
    shannon_index: float = Field(
        default=0.0, description="Shannon diversity index value"
    )
    shannon_range: str = Field(
        default="", description="Clinical range for Shannon index (e.g. 'High', 'Low')"
    )

class BacterialComposition(BaseModel):
    """Clinical interpretation of the taxonomic composition."""

    gender: str = Field(
        ..., description="Taxonomic unit (e.g. 'Firmicutes', 'Bacteroidetes', 'Escherichia coli')"
    )
    presence: str = Field(
        ..., description="Presence status of the taxonomic unit (e.g. 'Not Detected', 'Low', 'Normal', 'High')"
    )
    clinical_implication: str = Field(..., description="Biological consequence")

class BacterialDiversity(BaseModel):
    """Bacterial diversity based on taxonomic composition and diversity indices."""

    diversity_headline: str = Field(
        ..., description="Summary headline for bacterial diversity status (e.g. 'Optimal Diversity', 'No extreme domination')"
    )
    clinical_implication: str = Field(..., description="Biological consequence")

class OpportunisticMicroorganisms(BaseModel):
    """Opportunistic microorganisms detected and their clinical implications."""

    microorganism: str = Field(
        ..., description="Opportunistic microorganism (e.g. 'Escherichia coli')"
    )
    abundance_status: str = Field(
        ..., description="Abundance status of the microorganism (e.g. 'Low', 'Normal', 'High')"
    )
    abundance_score: int = Field(
        ..., description="Quantitative score supporting the abundance status (e.g. 0-100)"
    )
    clinical_implication: str = Field(..., description="Biological consequence")

class InferredMetabolicFunctions(BaseModel):
    """Inferred metabolic functions based on bacterial abundance."""

    metabolic_function: str = Field(
        ..., description="Metabolic function (e.g. 'Butyrate Production')"
    )
    activity_status: str = Field(
        ..., description="Activity level (e.g. 'Reduced', 'Normal', 'Enhanced')"
    )
    activity_score: int = Field(
        ..., description="Quantitative score supporting the activity status (e.g. 0-100)"
    )
    clinical_implication: str = Field(..., description="Biological consequence")

class ConclusionTags(BaseModel):
    """Tags summarizing key clinical conclusions."""

    tag: str = Field(..., description="Short tag summarizing key clinical conclusions (e.g. 'Dysbiosis', 'Optimal Diversity')")
    
class FinalObservations(BaseModel):
    """Final technical observations and conclusions based on the microbiota analysis."""

    conclusions: str = Field(
        ..., description="Summary of the final conclusions based on the microbiota status"
    )
    conclusion_tags: list[str] = Field(
        default_factory=list, description="Short tags summarizing key clinical conclusions (e.g. 'Dysbiosis', 'Optimal Diversity')"
    )
    global_indicator: str = Field(
        ..., description="Overall clinical indicator (e.g. 'Optimal', 'Needs Improvement')"
    )
    risk_score: int = Field(
        ..., description="Quantitative score supporting the overall risk of the patient based on the microbiota status (e.g. 0-100)"
    )

class MicrobiotaInterpretation(BaseModel):
    """Esquema de análisis clínico de los datos de microbiota realizado por la IA"""

    general_summary: GeneralSummary = Field(...)
    bacterial_composition: list[BacterialComposition] = Field(default_factory=list)
    bacterial_diversity: list[BacterialDiversity] = Field(default_factory=list)
    opportunistic_microorganisms: list[OpportunisticMicroorganisms] = Field(default_factory=list)
    inferred_metabolic_functions: list[InferredMetabolicFunctions] = Field(default_factory=list)
    final_observations: FinalObservations = Field(...)

class AnalysisReport(BaseModel):
    """Esquema que se va a guardar en la base de datos y retornar a Backend Nest"""
    
    study_id: str = Field(..., description="Unique identifier for the study")
    study_code: str = Field(..., description="Study code associated with the report")
    nutricionist_id: str = Field(..., description="Nutritionist information for validation and association")
    patient_id: str = Field(..., description="Patient associated with the report")
    data: MicrobiotaInput = Field(..., description="Extracted microbiota data")
    interpretation: MicrobiotaInterpretation = Field(..., description="Interpreted microbiota data")
    file_url: str = Field(..., description="URL from the generated PDF report")
    study_date: datetime = Field(..., description="Date when the study was created")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Timestamp when the report was created")

class AnalysisReportDB(BaseModel):
    """Esquema del informe a entregar después de guardar en la base de datos"""

    study_code: str = Field(..., description="Study code associated with the report")
    nutricionist_id: str = Field(..., description="Nutritionist information for validation and association")
    patient_id: str = Field(..., description="Patient associated with the report")
    data: MicrobiotaInput = Field(..., description="Extracted microbiota data")
    interpretation: MicrobiotaInterpretation = Field(..., description="Interpreted microbiota data")
    file_url: str = Field(..., description="URL from the generated PDF report")
    study_date: str = Field(..., description="Date when the study was created")
    created_at: str = Field(..., description="Timestamp when the report was created")