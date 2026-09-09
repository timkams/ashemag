"""
NCERT Class 9-12 Biology Chapter Catalog and Metadata Registry.
Covers:
- Class 9 Science (Biology Chapters)
- Class 10 Science (Biology Chapters)
- Class 11 Biology (Complete 22 Chapters)
- Class 12 Biology (Complete 16 Chapters)
"""
from typing import Dict, List, Any

NCERT_CHAPTERS: List[Dict[str, Any]] = [
    # ================= CLASS 9 (iesc1) =================
    {
        "grade": 9,
        "subject": "Science",
        "book_code": "iesc1",
        "chapter_num": 5,
        "filename": "iesc105.pdf",
        "title": "The Fundamental Unit of Life",
        "unit": "Organization in the Living World",
        "tags": ["cell", "plasma membrane", "nucleus", "mitochondria", "plastids", "endoplasmic reticulum", "golgi apparatus", "lysosomes", "vacuoles"]
    },
    {
        "grade": 9,
        "subject": "Science",
        "book_code": "iesc1",
        "chapter_num": 6,
        "filename": "iesc106.pdf",
        "title": "Tissues",
        "unit": "Organization in the Living World",
        "tags": ["plant tissues", "meristematic", "permanent", "parenchyma", "collenchyma", "sclerenchyma", "xylem", "phloem", "animal tissues", "epithelial", "connective", "muscular", "nervous"]
    },
    {
        "grade": 9,
        "subject": "Science",
        "book_code": "iesc1",
        "chapter_num": 7,
        "filename": "iesc107.pdf",
        "title": "Diversity in Living Organisms",
        "unit": "Diversity in the Living World",
        "tags": ["classification", "monera", "protista", "fungi", "plantae", "animalia", "porifera", "coelenterata", "chordata", "vertebrates"]
    },
    {
        "grade": 9,
        "subject": "Science",
        "book_code": "iesc1",
        "chapter_num": 13,
        "filename": "iesc113.pdf",
        "title": "Why Do We Fall Ill?",
        "unit": "Health and Diseases",
        "tags": ["health", "disease", "infectious", "pathogens", "immune system", "antibiotics", "vaccination", "prevention"]
    },
    {
        "grade": 9,
        "subject": "Science",
        "book_code": "iesc1",
        "chapter_num": 14,
        "filename": "iesc114.pdf",
        "title": "Natural Resources",
        "unit": "Our Environment",
        "tags": ["air", "water", "soil", "biogeochemical cycles", "water cycle", "nitrogen cycle", "carbon cycle", "oxygen cycle", "ozone layer"]
    },
    {
        "grade": 9,
        "subject": "Science",
        "book_code": "iesc1",
        "chapter_num": 15,
        "filename": "iesc115.pdf",
        "title": "Improvement in Food Resources",
        "unit": "Food Production",
        "tags": ["crop production", "manures", "fertilizers", "irrigation", "cropping patterns", "crop protection", "animal husbandry", "cattle", "poultry", "fisheries", "beekeeping"]
    },

    # ================= CLASS 10 (jesc1) =================
    {
        "grade": 10,
        "subject": "Science",
        "book_code": "jesc1",
        "chapter_num": 6,
        "filename": "jesc106.pdf",
        "title": "Life Processes",
        "unit": "World of Living",
        "tags": ["nutrition", "autotrophic", "heterotrophic", "photosynthesis", "human digestive system", "respiration", "aerobic", "anaerobic", "human heart", "double circulation", "blood vessels", "transport in plants", "excretion", "human nephron", "kidney"]
    },
    {
        "grade": 10,
        "subject": "Science",
        "book_code": "jesc1",
        "chapter_num": 7,
        "filename": "jesc107.pdf",
        "title": "Control and Coordination",
        "unit": "World of Living",
        "tags": ["nervous system", "neuron", "reflex arc", "human brain", "forebrain", "midbrain", "hindbrain", "plant movements", "tropism", "auxin", "gibberellin", "cytokinin", "abscisic acid", "endocrine glands", "hormones", "pituitary", "thyroid", "adrenal", "insulin"]
    },
    {
        "grade": 10,
        "subject": "Science",
        "book_code": "jesc1",
        "chapter_num": 8,
        "filename": "jesc108.pdf",
        "title": "How do Organisms Reproduce?",
        "unit": "World of Living",
        "tags": ["asexual reproduction", "fission", "fragmentation", "regeneration", "budding", "vegetative propagation", "spore formation", "sexual reproduction in plants", "flower structure", "pollination", "fertilization", "human reproductive system", "male reproductive system", "female reproductive system", "menstrual cycle", "contraception"]
    },
    {
        "grade": 10,
        "subject": "Science",
        "book_code": "jesc1",
        "chapter_num": 9,
        "filename": "jesc109.pdf",
        "title": "Heredity and Evolution",
        "unit": "World of Living",
        "tags": ["heredity", "traits", "mendel experiments", "monohybrid", "dihybrid", "sex determination", "speciation", "evolution", "homologous organs", "analogous organs", "fossils"]
    },
    {
        "grade": 10,
        "subject": "Science",
        "book_code": "jesc1",
        "chapter_num": 15,
        "filename": "jesc115.pdf",
        "title": "Our Environment",
        "unit": "Natural Resources",
        "tags": ["ecosystem", "producers", "consumers", "decomposers", "food chain", "food web", "trophic levels", "ten percent law", "biological magnification", "ozone layer depletion", "waste management"]
    },
    {
        "grade": 10,
        "subject": "Science",
        "book_code": "jesc1",
        "chapter_num": 16,
        "filename": "jesc116.pdf",
        "title": "Management of Natural Resources",
        "unit": "Natural Resources",
        "tags": ["natural resources", "forests", "wildlife", "water harvesting", "dams", "coal", "petroleum", "sustainable management"]
    },

    # ================= CLASS 11 BIOLOGY (kebo1) =================
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 1,
        "filename": "kebo101.pdf",
        "title": "The Living World",
        "unit": "Diversity in the Living World",
        "tags": ["living characteristics", "biodiversity", "taxonomy", "systematics", "binomial nomenclature", "taxonomic categories", "taxonomical aids", "herbarium", "botanical gardens", "museum", "zoological parks", "key"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 2,
        "filename": "kebo102.pdf",
        "title": "Biological Classification",
        "unit": "Diversity in the Living World",
        "tags": ["five kingdom classification", "monera", "bacteria", "protista", "fungi", "phycomycetes", "ascomycetes", "basidiomycetes", "deuteromycetes", "viruses", "viroids", "prions", "lichens"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 3,
        "filename": "kebo103.pdf",
        "title": "Plant Kingdom",
        "unit": "Diversity in the Living World",
        "tags": ["algae", "bryophytes", "pteridophytes", "gymnosperms", "angiosperms", "alternation of generations", "haplontic", "diplontic", "haplo-diplontic"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 4,
        "filename": "kebo104.pdf",
        "title": "Animal Kingdom",
        "unit": "Diversity in the Living World",
        "tags": ["levels of organization", "symmetry", "coelom", "porifera", "cnidaria", "ctenophora", "platyhelminthes", "aschelminthes", "annelida", "arthropoda", "mollusca", "echinodermata", "chordata", "vertebrata", "pisces", "amphibia", "reptilia", "aves", "mammalia"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 5,
        "filename": "kebo105.pdf",
        "title": "Morphology of Flowering Plants",
        "unit": "Structural Organisation in Plants and Animals",
        "tags": ["root", "stem", "leaf", "venation", "inflorescence", "flower parts", "aestivation", "placentation", "fruit", "seed", "fabaceae", "solanaceae", "liliaceae"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 6,
        "filename": "kebo106.pdf",
        "title": "Anatomy of Flowering Plants",
        "unit": "Structural Organisation in Plants and Animals",
        "tags": ["meristematic tissues", "permanent tissues", "tissue system", "epidermal", "ground", "vascular", "dicot root", "monocot root", "dicot stem", "monocot stem", "isobilateral leaf", "dorsiventral leaf", "secondary growth", "vascular cambium", "cork cambium"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 7,
        "filename": "kebo107.pdf",
        "title": "Structural Organisation in Animals",
        "unit": "Structural Organisation in Plants and Animals",
        "tags": ["animal tissues", "epithelial tissue", "connective tissue", "muscle tissue", "neural tissue", "earthworm", "cockroach morphology and anatomy", "frog morphology and anatomy"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 8,
        "filename": "kebo108.pdf",
        "title": "Cell: The Unit of Life",
        "unit": "Cell: Structure and Functions",
        "tags": ["cell theory", "prokaryotic cell", "eukaryotic cell", "cell membrane", "fluid mosaic model", "cell wall", "endoplasmic reticulum", "golgi apparatus", "lysosomes", "vacuoles", "mitochondria", "plastids", "ribosomes", "cytoskeleton", "cilia and flagella", "centrosome", "nucleus", "chromosomes"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 9,
        "filename": "kebo109.pdf",
        "title": "Biomolecules",
        "unit": "Cell: Structure and Functions",
        "tags": ["primary and secondary metabolites", "biomacromolecules", "proteins", "polysaccharides", "nucleic acids", "structure of proteins", "enzymes", "chemical reactions", "factors affecting enzyme activity", "enzyme classification", "co-factors"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 10,
        "filename": "kebo110.pdf",
        "title": "Cell Cycle and Cell Division",
        "unit": "Cell: Structure and Functions",
        "tags": ["cell cycle", "phases of cell cycle", "interphase", "m phase", "mitosis", "prophase", "metaphase", "anaphase", "telophase", "cytokinesis", "meiosis", "meiosis I", "meiosis II", "significance of mitosis and meiosis"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 11,
        "filename": "kebo111.pdf",
        "title": "Transport in Plants",
        "unit": "Plant Physiology",
        "tags": ["diffusion", "facilitated diffusion", "active transport", "water potential", "osmosis", "plasmolysis", "imbibition", "long distance transport", "apoplast", "symplast", "transpiration pull", "phloem transport"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 12,
        "filename": "kebo112.pdf",
        "title": "Mineral Nutrition",
        "unit": "Plant Physiology",
        "tags": ["essential mineral elements", "macronutrients", "micronutrients", "deficiency symptoms", "toxicity", "nitrogen cycle", "biological nitrogen fixation", "nodule formation", "nitrogenase enzyme"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 13,
        "filename": "kebo113.pdf",
        "title": "Photosynthesis in Higher Plants",
        "unit": "Plant Physiology",
        "tags": ["chloroplast pigments", "light reaction", "electron transport", "photophosphorylation", "z scheme", "chemiosmotic hypothesis", "calvin cycle", "c3 pathway", "c4 pathway", "krantz anatomy", "photorespiration", "blackman law of limiting factors"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 14,
        "filename": "kebo114.pdf",
        "title": "Respiration in Plants",
        "unit": "Plant Physiology",
        "tags": ["cellular respiration", "glycolysis", "fermentation", "aerobic respiration", "tricarboxylic acid cycle", "krebs cycle", "electron transport system", "oxidative phosphorylation", "respiratory balance sheet", "amphibolic pathway", "respiratory quotient"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 15,
        "filename": "kebo115.pdf",
        "title": "Plant Growth and Development",
        "unit": "Plant Physiology",
        "tags": ["growth rate", "differentiation", "dedifferentiation", "redifferentiation", "development", "plant growth regulators", "auxins", "gibberellins", "cytokinins", "ethylene", "abscisic acid", "photoperiodism", "vernalisation"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 16,
        "filename": "kebo116.pdf",
        "title": "Digestion and Absorption",
        "unit": "Human Physiology",
        "tags": ["human digestive system", "alimentary canal", "teeth", "stomach", "small intestine", "large intestine", "digestive glands", "salivary glands", "liver", "pancreas", "digestion of food", "absorption of digested products", "disorders of digestive system"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 17,
        "filename": "kebo117.pdf",
        "title": "Breathing and Exchange of Gases",
        "unit": "Human Physiology",
        "tags": ["respiratory organs", "human respiratory system", "mechanism of breathing", "respiratory volumes and capacities", "exchange of gases", "transport of gases", "oxygen-haemoglobin dissociation curve", "regulation of respiration", "disorders of respiratory system", "asthma", "emphysema"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 18,
        "filename": "kebo118.pdf",
        "title": "Body Fluids and Circulation",
        "unit": "Human Physiology",
        "tags": ["blood", "plasma", "formed elements", "erythrocytes", "leukocytes", "platelets", "blood groups", "abo system", "rh grouping", "coagulation of blood", "lymph", "circulatory pathways", "human circulatory system", "structure of heart", "cardiac cycle", "electrocardiograph", "ecg", "double circulation", "regulation of cardiac activity", "disorders of circulatory system", "hypertension", "coronary artery disease", "angina", "heart failure"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 19,
        "filename": "kebo119.pdf",
        "title": "Excretory Products and their Elimination",
        "unit": "Human Physiology",
        "tags": ["modes of excretion", "ammonotelism", "ureotelism", "uricotelism", "human excretory system", "kidney structure", "nephron", "cortical and juxtamedullary nephrons", "urine formation", "glomerular filtration", "tubular reabsorption", "tubular secretion", "function of tubules", "counter current mechanism", "regulation of kidney function", "juxtaglomerular apparatus", "raas", "anf", "micturition", "role of other organs in excretion", "disorders of excretory system", "uremia", "renal calculi", "dialysis"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 20,
        "filename": "kebo120.pdf",
        "title": "Locomotion and Movement",
        "unit": "Human Physiology",
        "tags": ["types of movement", "muscle", "skeletal muscle", "visceral muscle", "cardiac muscle", "structure of contractile proteins", "actin", "myosin", "sliding filament theory", "skeletal system", "axial skeleton", "skull", "vertebral column", "ribs", "sternum", "appendicular skeleton", "pectoral and pelvic girdle", "limbs", "joints", "synovial joints", "disorders of muscular and skeletal system", "myasthenia gravis", "tetany", "arthritis", "osteoporosis", "gout"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 21,
        "filename": "kebo121.pdf",
        "title": "Neural Control and Coordination",
        "unit": "Human Physiology",
        "tags": ["neural system", "human neural system", "cns", "pns", "neuron as structural and functional unit", "generation and conduction of nerve impulses", "synapse", "chemical and electrical synapse", "central nervous system", "human brain", "forebrain", "cerebrum", "thalamus", "hypothalamus", "midbrain", "hindbrain", "cerebellum", "pons", "medulla", "reflex action and reflex arc", "sensory reception and processing", "eye structure and vision", "ear structure and hearing"]
    },
    {
        "grade": 11,
        "subject": "Biology",
        "book_code": "kebo1",
        "chapter_num": 22,
        "filename": "kebo122.pdf",
        "title": "Chemical Coordination and Integration",
        "unit": "Human Physiology",
        "tags": ["endocrine glands and hormones", "human endocrine system", "hypothalamus", "pituitary gland", "pineal gland", "thyroid gland", "parathyroid gland", "thymus", "adrenal gland", "pancreas", "islets of langerhans", "testis", "ovary", "hormones of heart kidney and gastrointestinal tract", "mechanism of hormone action", "peptide hormones", "steroid hormones"]
    },

    # ================= CLASS 12 BIOLOGY (lebo1) =================
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 1,
        "filename": "lebo101.pdf",
        "title": "Reproduction in Organisms",
        "unit": "Reproduction",
        "tags": ["life span", "asexual reproduction", "sexual reproduction", "pre-fertilization events", "gametogenesis", "gamete transfer", "fertilization", "post-fertilization events", "zygote", "embryogenesis"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 2,
        "filename": "lebo102.pdf",
        "title": "Sexual Reproduction in Flowering Plants",
        "unit": "Reproduction",
        "tags": ["flower", "pre-fertilization structures and events", "stamen", "microsporangium", "pollen grain", "pistil", "megasporangium", "ovule", "embryo sac", "pollination", "outbreeding devices", "pollen-pistil interaction", "double fertilization", "post-fertilization", "endosperm", "embryo", "seed", "apomixis", "polyembryony"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 3,
        "filename": "lebo103.pdf",
        "title": "Human Reproduction",
        "unit": "Reproduction",
        "tags": ["male reproductive system", "testes", "seminiferous tubules", "sertoli cells", "leydig cells", "female reproductive system", "ovaries", "fallopian tubes", "uterus", "gametogenesis", "spermatogenesis", "sperm structure", "oogenesis", "menstrual cycle", "hormonal control", "fertilization and implantation", "pregnancy and embryonic development", "placenta", "parturition and lactation"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 4,
        "filename": "lebo104.pdf",
        "title": "Reproductive Health",
        "unit": "Reproduction",
        "tags": ["reproductive health problems and strategies", "population explosion and birth control", "contraceptive methods", "medical termination of pregnancy", "mtp", "sexually transmitted infections", "infertility", "assisted reproductive technologies", "art", "ivf", "icsi", "gift", "zift"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 5,
        "filename": "lebo105.pdf",
        "title": "Principles of Inheritance and Variation",
        "unit": "Genetics and Evolution",
        "tags": ["mendel laws of inheritance", "law of dominance", "law of segregation", "law of independent assortment", "incomplete dominance", "co-dominance", "multiple alleles", "chromosomal theory of inheritance", "linkage and recombination", "sex determination", "mutation", "pedigree analysis", "mendelian disorders", "hemophilia", "sickle-cell anemia", "phenylketonuria", "chromosomal disorders", "down syndrome", "klinefelter syndrome", "turner syndrome"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 6,
        "filename": "lebo106.pdf",
        "title": "Molecular Basis of Inheritance",
        "unit": "Genetics and Evolution",
        "tags": ["dna structure", "double helix model", "packaging of dna helix", "search for genetic material", "griffith experiment", "hershey-chase experiment", "dna replication", "meselson-stahl experiment", "transcription", "transcription unit", "genetic code", "tRNA adapter molecule", "translation", "regulation of gene expression", "lac operon", "human genome project", "dna fingerprinting"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 7,
        "filename": "lebo107.pdf",
        "title": "Evolution",
        "unit": "Genetics and Evolution",
        "tags": ["origin of life", "oparin-haldane hypothesis", "miller experiment", "evolution of life forms", "evidences for evolution", "paleontological", "comparative anatomy", "adaptive radiation", "darwinian theory", "mutation theory of hugo de vries", "hardy-weinberg principle", "natural selection types", "origin and evolution of man"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 8,
        "filename": "lebo108.pdf",
        "title": "Human Health and Disease",
        "unit": "Biology in Human Welfare",
        "tags": ["common diseases in humans", "typhoid", "pneumonia", "malaria life cycle", "amoebiasis", "ringworms", "immunity", "innate immunity", "acquired immunity", "active and passive immunity", "vaccination and immunization", "allergies", "autoimmunity", "immune system in body", "aids", "hiv", "cancer", "carcinogens", "drugs and alcohol abuse"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 9,
        "filename": "lebo109.pdf",
        "title": "Strategies for Enhancement in Food Production",
        "unit": "Biology in Human Welfare",
        "tags": ["animal husbandry", "management of farms", "animal breeding", "bee-keeping", "fisheries", "plant breeding", "breeding for disease resistance", "biofortification", "single cell protein", "tissue culture", "micropropagation", "somatic hybrids"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 10,
        "filename": "lebo110.pdf",
        "title": "Microbes in Human Welfare",
        "unit": "Biology in Human Welfare",
        "tags": ["microbes in household products", "microbes in industrial products", "fermentation", "antibiotics", "microbes in sewage treatment", "primary and secondary treatment", "microbes in production of biogas", "methanogens", "microbes as biocontrol agents", "microbes as biofertilisers", "mycorrhiza", "cyanobacteria"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 11,
        "filename": "lebo111.pdf",
        "title": "Biotechnology: Principles and Processes",
        "unit": "Biotechnology",
        "tags": ["principles of biotechnology", "genetic engineering", "restriction enzymes", "cloning vectors", "plasmids", "competent host", "processes of recombinant dna technology", "isolation of dna", "polymerase chain reaction", "pcr", "bioreactors", "downstream processing"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 12,
        "filename": "lebo112.pdf",
        "title": "Biotechnology and its Applications",
        "unit": "Biotechnology",
        "tags": ["biotechnological applications in agriculture", "bt crops", "bt cotton", "pest resistant plants", "rnai", "biotechnological applications in medicine", "genetically engineered insulin", "gene therapy", "molecular diagnosis", "transgenic animals", "ethical issues", "biopiracy"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 13,
        "filename": "lebo113.pdf",
        "title": "Organisms and Populations",
        "unit": "Ecology",
        "tags": ["organism and its environment", "major abiotic factors", "responses to abiotic factors", "regulators", "conformers", "adaptations", "populations", "population attributes", "population growth models", "exponential growth", "logistic growth", "population interactions", "predation", "competition", "parasitism", "commensalism", "mutualism"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 14,
        "filename": "lebo114.pdf",
        "title": "Ecosystem",
        "unit": "Ecology",
        "tags": ["ecosystem structure and function", "productivity", "gross and net primary productivity", "decomposition", "energy flow", "ecological pyramids", "pyramid of numbers", "pyramid of biomass", "pyramid of energy", "ecological succession", "nutrient cycling", "carbon cycle", "phosphorus cycle", "ecosystem services"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 15,
        "filename": "lebo115.pdf",
        "title": "Biodiversity and Conservation",
        "unit": "Ecology",
        "tags": ["biodiversity", "levels of biodiversity", "patterns of biodiversity", "latitudinal gradients", "species-area relationships", "importance of species diversity", "loss of biodiversity", "the evil quartet", "biodiversity conservation", "in-situ conservation", "ex-situ conservation", "biosphere reserves", "national parks", "sacred groves"]
    },
    {
        "grade": 12,
        "subject": "Biology",
        "book_code": "lebo1",
        "chapter_num": 16,
        "filename": "lebo116.pdf",
        "title": "Environmental Issues",
        "unit": "Ecology",
        "tags": ["pollution", "air pollution and its control", "catalytic converters", "water pollution and its control", "bod", "biomagnification", "eutrophication", "solid wastes", "radioactive wastes", "greenhouse effect and global warming", "ozone depletion in stratosphere", "cfcs", "deforestation", "reforestation"]
    }
]

def get_chapters_by_grade(grade: int) -> List[Dict[str, Any]]:
    return [ch for ch in NCERT_CHAPTERS if ch["grade"] == grade]

def get_chapter(grade: int, chapter_num: int) -> Dict[str, Any]:
    for ch in NCERT_CHAPTERS:
        if ch["grade"] == grade and ch["chapter_num"] == chapter_num:
            return ch
    return {}
