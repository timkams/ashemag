/**
 * Human Atlas & NCERT Biology Translations (English & Hindi).
 */

export type Language = 'en' | 'hi';

export const TRANSLATIONS = {
  en: {
    // Header & Identity
    brandEyebrow: 'INTERACTIVE ANATOMY',
    edition: '3D',
    modeledPieces: 'modeled pieces',
    bodyParts3d: 'BodyParts3D',

    // Top Navigation
    findStructure: 'Find a structure',
    bioAiTutor: 'Bio AI Tutor',
    aboutAtlas: 'About this atlas',

    // Systems Panel
    systems: 'Systems',
    all: 'All',
    skeleton: 'Skeleton',
    organs: 'Organs',
    piecesVisible: 'pieces visible',
    hideAll: 'Hide all',
    closeSystems: 'Close systems',

    // System Names
    systemNames: {
      skeletal: 'Skeleton',
      muscular: 'Muscles',
      cardiac: 'Heart',
      arterial: 'Arteries',
      venous: 'Veins',
      nervous: 'Nervous system',
      sensory: 'Sensory organs',
      respiratory: 'Lungs & airway',
      digestive: 'Digestive system',
      urinary: 'Urinary system',
      reproductive: 'Reproductive',
      endocrine: 'Endocrine',
      lymphatic: 'Lymphatic',
      integumentary: 'Skin & hair',
      connective: 'Connective tissue'
    } as Record<string, string>,

    // Search Panel
    searchPlaceholder: 'Heart, femur, cranial nerve…',
    noStructuresMatch: 'No structures match your search.',
    searchNoteActive: 'Showing up to 80 matches. Refine your search to find smaller structures.',
    searchNoteEmpty: 'Start with a major organ, or search every named structure.',
    closeSearch: 'Close search',
    piece: 'piece',
    pieces: 'pieces',

    // View & Camera Controls
    threeQuarterView: '¾ view',
    frontView: 'Front view',
    sideView: 'Side view',
    backView: 'Back view',
    autoRotate: 'Auto rotate',
    pauseRotation: 'Pause rotation',
    resetView: 'Reset view and layers',
    darkMode: 'Toggle dark mode',
    languageToggle: 'भाषा बदलें (Switch to Hindi)',

    // Scene Caption
    adultHumanMale: 'ADULT HUMAN · MALE',
    separatedStructures: 'SEPARATED STRUCTURES',
    anatomicalInventory: 'ANATOMICAL INVENTORY',
    selectedStructure: 'SELECTED STRUCTURE',

    // Bottom Dock & Explode
    systemsButton: 'Systems',
    explodeAnatomy: 'Explode anatomy',
    assembled: 'Assembled',
    everyPiece: 'Every piece',
    reset: 'Reset',

    // Footer
    dragToOrbit: 'Drag to orbit',
    dragToPan: 'Drag to pan',
    pinchToZoom: 'Pinch to zoom',
    tapToInspect: 'Tap to inspect',
    bioAiAndScope: 'Bio AI Tutor & Scope',

    // Loading & Error
    preparingAnatomy: 'Preparing the anatomy',
    loadingPieces: 'Loading pieces',
    reloadViewer: 'Reload viewer',

    // Detail Sheet
    anatomyHeader: 'ANATOMY',
    systemOverview: 'System overview · structure identified from source anatomy',
    atlasReference: 'Atlas reference',
    selectedPieces: 'Selected pieces',
    includedStructures: 'Included structures',
    andMorePieces: 'more modeled pieces.',
    viewAnatomicalSource: 'View anatomical source',
    isolateStructure: 'Isolate structure',
    showSurrounding: 'Show surrounding anatomy',
    clearSelection: 'Clear selection',

    // Prompt Dock & Chatbot
    dockPlaceholder: 'Ask Gemini about anatomy & NCERT biology (e.g. nephron, heart, DNA)...',
    dockModelTag: '✦ Gemini + NCERT',
    dockSearching: 'Searching NCERT Central Knowledge Base:',
    sidebarOpenBadge: 'Sidebar Open',
    chatTitle: '✦ GEMINI & NCERT BIOLOGY TUTOR',
    chatSubtitleGrounded: 'Grounded with Gemini 1.5 Flash · Class 9–12 KB',
    chatSubtitleLocal: 'Central Knowledge Base · Official NCERT Class 9–12',
    chatClear: 'Clear',
    chatClassLabel: 'Class:',
    chatAllClass: 'All',
    chatAsk3dFocus: 'Ask about 3D focus:',
    chatInputPlaceholder: 'Ask biology questions (e.g. nephron, heart, mitosis)...',
    chatCitations: 'NCERT textbook citations',
    chatSingleCitation: 'NCERT textbook citation',
    chatWelcome: 'Hello! I am your NCERT Biology Assistant. Ask me anything about human anatomy, organ systems, cellular biology, genetics, or physiology from Class 9 to 12 textbooks.',
    chatSuggestionsLabel: 'Suggestions:',
    quickPrompts: [
      'How do kidneys filter blood and form urine?',
      'Describe double circulation in human beings',
      'What is the powerhouse of the cell?',
      'What happens during cardiac cycle?',
      'Explain DNA double helix model'
    ]
  },

  hi: {
    // Header & Identity
    brandEyebrow: 'इंटरैक्टिव मानव शरीर रचना',
    edition: '3D',
    modeledPieces: 'मॉडल किए गए अंग',
    bodyParts3d: 'BodyParts3D',

    // Top Navigation
    findStructure: 'संरचना खोजें',
    bioAiTutor: 'बायो एआई ट्यूटर',
    aboutAtlas: 'एटलस के बारे में',

    // Systems Panel
    systems: 'शारीरिक तंत्र',
    all: 'सभी',
    skeleton: 'कंकाल',
    organs: 'अंग',
    piecesVisible: 'अंग दृश्यमान',
    hideAll: 'सभी छिपाएं',
    closeSystems: 'तंत्र बंद करें',

    // System Names
    systemNames: {
      skeletal: 'कंकाल तंत्र',
      muscular: 'पेशी तंत्र',
      cardiac: 'हृदय',
      arterial: 'धमनियां',
      venous: 'शिराएं',
      nervous: 'तंत्रिका तंत्र',
      sensory: 'संवेदी अंग',
      respiratory: 'श्वसन तंत्र',
      digestive: 'पाचन तंत्र',
      urinary: 'उत्सर्जन तंत्र',
      reproductive: 'प्रजनन तंत्र',
      endocrine: 'अंतःस्रावी तंत्र',
      lymphatic: 'लसीका तंत्र',
      integumentary: 'त्वचा तंत्र',
      connective: 'संयोजी ऊतक'
    } as Record<string, string>,

    // Search Panel
    searchPlaceholder: 'हृदय, फीमर, कपाल तंत्रिका…',
    noStructuresMatch: 'आपकी खोज से कोई संरचना मेल नहीं खाती।',
    searchNoteActive: 'अधिकतम 80 परिणाम दिखाए जा रहे हैं। छोटी संरचनाओं के लिए खोज को विशिष्ट बनाएं।',
    searchNoteEmpty: 'प्रमुख अंग से शुरुआत करें या किसी भी संरचना को खोजें।',
    closeSearch: 'खोज बंद करें',
    piece: 'भाग',
    pieces: 'भाग',

    // View & Camera Controls
    threeQuarterView: '¾ दृश्य',
    frontView: 'सामने का दृश्य',
    sideView: 'पार्श्व दृश्य',
    backView: 'पीछे का दृश्य',
    autoRotate: 'घूर्णन चालू करें',
    pauseRotation: 'घूर्णन रोकें',
    resetView: 'दृश्य व परतें रीसेट करें',
    darkMode: 'डार्क मोड बदलें',
    languageToggle: 'Switch to English',

    // Scene Caption
    adultHumanMale: 'वयस्क मानव · पुरुष',
    separatedStructures: 'अलग की गई संरचनाएं',
    anatomicalInventory: 'शारीरिक संरचना सूची',
    selectedStructure: 'चयनित संरचना',

    // Bottom Dock & Explode
    systemsButton: 'तंत्र',
    explodeAnatomy: 'संरचना का विस्तार',
    assembled: 'संयोजित',
    everyPiece: 'प्रत्येक अंग',
    reset: 'रीसेट',

    // Footer
    dragToOrbit: 'घुमाने के लिए ड्रैग करें',
    dragToPan: 'पैन करने के लिए ड्रैग करें',
    pinchToZoom: 'ज़ूम करने के लिए पिंच करें',
    tapToInspect: 'निरीक्षण के लिए टैप करें',
    bioAiAndScope: 'बायो एआई व दायरा',

    // Loading & Error
    preparingAnatomy: 'शरीर रचना तैयार हो रही है',
    loadingPieces: 'अंग लोड हो रहे हैं',
    reloadViewer: 'व्यूअर पुनः लोड करें',

    // Detail Sheet
    anatomyHeader: 'शरीर रचना',
    systemOverview: 'तंत्र अवलोकन · स्रोत से पहचानी गई संरचना',
    atlasReference: 'एटलस संदर्भ',
    selectedPieces: 'चयनित टुकड़े',
    includedStructures: 'शामिल संरचनाएं',
    andMorePieces: 'और अन्य अंग।',
    viewAnatomicalSource: 'शारीरिक स्रोत देखें',
    isolateStructure: 'संरचना अलग करें',
    showSurrounding: 'आसपास की संरचनाएं दिखाएं',
    clearSelection: 'चयन हटाएं',

    // Prompt Dock & Chatbot
    dockPlaceholder: 'मानव शरीर रचना व एनसीईआरटी जीव विज्ञान के बारे में पूछें...',
    dockModelTag: '✦ जेमिनी + एनसीईआरटी',
    dockSearching: 'एनसीईआरटी केंद्रीय ज्ञानकोष से खोज जारी है:',
    sidebarOpenBadge: 'साइडबार खुला',
    chatTitle: '✦ जेमिनी एवं एनसीईआरटी जीव विज्ञान ट्यूटर',
    chatSubtitleGrounded: 'कक्षा 9–12 एनसीईआरटी ज्ञानकोष से प्रमाणित उत्तर',
    chatSubtitleLocal: 'केंद्रीय ज्ञानकोष · आधिकारिक एनसीईआरटी कक्षा 9–12',
    chatClear: 'साफ़ करें',
    chatClassLabel: 'कक्षा:',
    chatAllClass: 'सभी',
    chatAsk3dFocus: '3D चयनित अंग के बारे में पूछें:',
    chatInputPlaceholder: 'जीव विज्ञान प्रश्न पूछें (जैसे वृक्क, हृदय, समसूत्री विभाजन)...',
    chatCitations: 'एनसीईआरटी पाठ्यपुस्तक संदर्भ',
    chatSingleCitation: 'एनसीईआरटी पाठ्यपुस्तक संदर्भ',
    chatWelcome: 'नमस्ते! मैं आपका एनसीईआरटी जीव विज्ञान सहायक हूँ। कक्षा 9 से 12 तक के मानव शरीर रचना, तंत्र, कोशिका विज्ञान, आनुवंशिकी या कार्यप्रणाली के बारे में कुछ भी पूछें।',
    chatSuggestionsLabel: 'सुझाव:',
    quickPrompts: [
      'वृक्क (किडनी) रक्त को कैसे छानता है और मूत्र बनाता है?',
      'मानव में दोहरा परिसंचरण समझाइए',
      'कोशिका का पावरहाउस किसे कहते हैं और क्यों?',
      'मानव हृदय में कार्डिएक चक्र के दौरान क्या होता है?',
      'डीएनए की डबल हेलिक्स संरचना समझाइए'
    ]
  }
};
