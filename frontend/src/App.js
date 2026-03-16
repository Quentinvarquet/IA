import { useState, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
    Shield, 
    Copy, 
    Check, 
    AlertTriangle, 
    Loader2, 
    FileJson,
    Eye,
    EyeOff,
    Trash2,
    Download
} from "lucide-react";
import { Button } from "./components/ui/button";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sample JSON for demo
const SAMPLE_JSON = {
    "utilisateur": {
        "nom": "Dupont",
        "prenom": "Jean-Pierre",
        "email": "jean.dupont@gmail.com",
        "telephone": "06 12 34 56 78",
        "adresse": "15 rue de la Paix",
        "code_postal": "75001",
        "ville": "Paris"
    },
    "informations_bancaires": {
        "iban": "FR76 3000 6000 0112 3456 7890 189",
        "titulaire": "Jean-Pierre Dupont"
    },
    "securite_sociale": {
        "numero_secu": "1 85 12 75 108 123 45",
        "date_naissance": "15/12/1985"
    },
    "contacts": [
        {
            "nom": "Martin",
            "prenom": "Marie",
            "email": "marie.martin@orange.fr",
            "telephone": "07 98 76 54 32"
        }
    ]
};

// JSON Syntax Highlighter Component
const JsonHighlight = ({ data }) => {
    const highlight = (obj, indent = 0) => {
        const spaces = "  ".repeat(indent);
        
        if (obj === null) {
            return <span className="json-null">null</span>;
        }
        
        if (typeof obj === "boolean") {
            return <span className="json-boolean">{obj.toString()}</span>;
        }
        
        if (typeof obj === "number") {
            return <span className="json-number">{obj}</span>;
        }
        
        if (typeof obj === "string") {
            return <span className="json-string">"{obj}"</span>;
        }
        
        if (Array.isArray(obj)) {
            if (obj.length === 0) return "[]";
            return (
                <>
                    {"[\n"}
                    {obj.map((item, i) => (
                        <span key={i}>
                            {spaces}{"  "}{highlight(item, indent + 1)}
                            {i < obj.length - 1 ? ",\n" : "\n"}
                        </span>
                    ))}
                    {spaces}{"]"}
                </>
            );
        }
        
        if (typeof obj === "object") {
            const keys = Object.keys(obj);
            if (keys.length === 0) return "{}";
            return (
                <>
                    {"{\n"}
                    {keys.map((key, i) => (
                        <span key={key}>
                            {spaces}{"  "}<span className="json-key">"{key}"</span>: {highlight(obj[key], indent + 1)}
                            {i < keys.length - 1 ? ",\n" : "\n"}
                        </span>
                    ))}
                    {spaces}{"}"}
                </>
            );
        }
        
        return String(obj);
    };
    
    return <pre className="m-0">{highlight(data)}</pre>;
};

// Field Type Labels in French
const FIELD_TYPE_LABELS = {
    nom: "Nom",
    prenom: "Prénom",
    nom_complet: "Nom complet",
    email: "Email",
    telephone: "Téléphone",
    adresse: "Adresse",
    code_postal: "Code postal",
    ville: "Ville",
    iban: "IBAN",
    secu: "N° Sécu",
    date_naissance: "Date naissance",
    carte_bancaire: "Carte bancaire"
};

function App() {
    const [inputJson, setInputJson] = useState("");
    const [outputData, setOutputData] = useState(null);
    const [detectedFields, setDetectedFields] = useState([]);
    const [stats, setStats] = useState({});
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);
    const [copied, setCopied] = useState(false);
    const [showOriginal, setShowOriginal] = useState(false);

    const handleAnonymize = useCallback(async () => {
        setError(null);
        setIsProcessing(true);
        
        try {
            // Parse JSON input
            let jsonData;
            try {
                jsonData = JSON.parse(inputJson);
            } catch (parseError) {
                throw new Error("JSON invalide. Veuillez vérifier la syntaxe.");
            }
            
            // Call API
            const response = await axios.post(`${API}/anonymize`, {
                data: jsonData
            });
            
            if (response.data.success) {
                setOutputData(response.data.anonymized_data);
                setDetectedFields(response.data.detected_fields);
                setStats(response.data.stats);
                
                const totalFields = response.data.detected_fields.length;
                if (totalFields > 0) {
                    toast.success(`${totalFields} champ(s) sensible(s) anonymisé(s)`);
                } else {
                    toast.info("Aucun champ sensible détecté");
                }
            }
        } catch (err) {
            const errorMessage = err.response?.data?.detail || err.message || "Erreur lors de l'anonymisation";
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setIsProcessing(false);
        }
    }, [inputJson]);

    const handleCopy = useCallback(() => {
        if (outputData) {
            navigator.clipboard.writeText(JSON.stringify(outputData, null, 2));
            setCopied(true);
            toast.success("JSON copié dans le presse-papier");
            setTimeout(() => setCopied(false), 2000);
        }
    }, [outputData]);

    const handleClear = useCallback(() => {
        setInputJson("");
        setOutputData(null);
        setDetectedFields([]);
        setStats({});
        setError(null);
    }, []);

    const handleLoadSample = useCallback(() => {
        setInputJson(JSON.stringify(SAMPLE_JSON, null, 2));
        setOutputData(null);
        setDetectedFields([]);
        setStats({});
        setError(null);
        toast.info("Exemple JSON chargé");
    }, []);

    const handleDownload = useCallback(() => {
        if (outputData) {
            const blob = new Blob([JSON.stringify(outputData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'anonymized_data.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            toast.success("Fichier téléchargé");
        }
    }, [outputData]);

    const totalDetected = detectedFields.length;

    return (
        <div className="min-h-screen bg-[#050505] grid-bg">
            <Toaster 
                theme="dark" 
                position="top-right"
                toastOptions={{
                    style: {
                        background: '#0f0f0f',
                        border: '1px solid #333',
                        color: '#eee',
                        fontFamily: 'JetBrains Mono, monospace',
                        borderRadius: '0'
                    }
                }}
            />
            
            {/* Header */}
            <header className="border-b border-[#333] bg-[#0a0a0a]">
                <div className="max-w-7xl mx-auto px-4 md:px-8 py-6">
                    <div className="flex items-center gap-4">
                        <div className="p-3 border border-[#00ff94]/30 bg-[#00ff94]/5">
                            <Shield className="w-8 h-8 text-[#00ff94]" data-testid="shield-icon" />
                        </div>
                        <div>
                            <h1 className="header-title text-2xl md:text-3xl text-[#eee]" data-testid="app-title">
                                JSON ANONYMIZER
                            </h1>
                            <p className="text-[#888] text-xs md:text-sm font-mono mt-1">
                                PROTECTION DES DONNÉES SENSIBLES // DÉTECTION AUTOMATIQUE
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 md:px-8 py-8">
                {/* Action Bar */}
                <div className="flex flex-wrap gap-3 mb-6">
                    <Button
                        onClick={handleLoadSample}
                        variant="outline"
                        className="btn-terminal font-mono text-xs uppercase tracking-wider border-[#333] hover:border-[#00ff94] hover:text-[#00ff94] bg-transparent"
                        data-testid="load-sample-btn"
                    >
                        <FileJson className="w-4 h-4 mr-2" />
                        Charger exemple
                    </Button>
                    <Button
                        onClick={handleClear}
                        variant="outline"
                        className="btn-terminal font-mono text-xs uppercase tracking-wider border-[#333] hover:border-[#ff3333] hover:text-[#ff3333] bg-transparent"
                        data-testid="clear-btn"
                    >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Effacer
                    </Button>
                </div>

                {/* Main Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Input Panel */}
                    <div className="border border-[#333] bg-[#0a0a0a]">
                        <div className="border-b border-[#333] px-4 py-3 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span className="text-[#ff3333] text-xs">●</span>
                                <span className="font-mono text-xs uppercase tracking-wider text-[#888]">
                                    SOURCE // DONNÉES ORIGINALES
                                </span>
                            </div>
                        </div>
                        <div className="p-4">
                            <textarea
                                value={inputJson}
                                onChange={(e) => setInputJson(e.target.value)}
                                placeholder='{\n  "nom": "Dupont",\n  "email": "jean@example.com",\n  "telephone": "06 12 34 56 78"\n}'
                                className="terminal-textarea w-full h-[350px]"
                                data-testid="json-input"
                                spellCheck={false}
                            />
                        </div>
                        <div className="border-t border-[#333] px-4 py-3">
                            <Button
                                onClick={handleAnonymize}
                                disabled={!inputJson.trim() || isProcessing}
                                className="w-full btn-terminal font-mono text-xs uppercase tracking-widest h-12 bg-[#00ff94] text-black hover:bg-[#00ff94]/90 disabled:opacity-50 disabled:cursor-not-allowed border-0"
                                data-testid="anonymize-btn"
                            >
                                {isProcessing ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        TRAITEMENT EN COURS...
                                    </>
                                ) : (
                                    <>
                                        <Shield className="w-4 h-4 mr-2" />
                                        ANONYMISER
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>

                    {/* Output Panel */}
                    <div className="border border-[#333] bg-[#0a0a0a]">
                        <div className="border-b border-[#333] px-4 py-3 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span className="text-[#00ff94] text-xs">●</span>
                                <span className="font-mono text-xs uppercase tracking-wider text-[#888]">
                                    OUTPUT // DONNÉES ANONYMISÉES
                                </span>
                            </div>
                            {outputData && (
                                <div className="flex items-center gap-2">
                                    <Button
                                        onClick={() => setShowOriginal(!showOriginal)}
                                        variant="ghost"
                                        size="sm"
                                        className="h-7 px-2 text-[#888] hover:text-[#00ff94] hover:bg-transparent"
                                        data-testid="toggle-view-btn"
                                    >
                                        {showOriginal ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </Button>
                                    <Button
                                        onClick={handleDownload}
                                        variant="ghost"
                                        size="sm"
                                        className="h-7 px-2 text-[#888] hover:text-[#00ff94] hover:bg-transparent"
                                        data-testid="download-btn"
                                    >
                                        <Download className="w-4 h-4" />
                                    </Button>
                                    <Button
                                        onClick={handleCopy}
                                        variant="ghost"
                                        size="sm"
                                        className="h-7 px-2 text-[#888] hover:text-[#00ff94] hover:bg-transparent"
                                        data-testid="copy-btn"
                                    >
                                        {copied ? <Check className="w-4 h-4 text-[#00ff94]" /> : <Copy className="w-4 h-4" />}
                                    </Button>
                                </div>
                            )}
                        </div>
                        <div className="p-4">
                            <div className="json-output h-[350px] overflow-auto scanlines" data-testid="json-output">
                                {error ? (
                                    <div className="flex items-center gap-3 text-[#ff3333]">
                                        <AlertTriangle className="w-5 h-5" />
                                        <span>{error}</span>
                                    </div>
                                ) : outputData ? (
                                    showOriginal ? (
                                        <JsonHighlight data={JSON.parse(inputJson)} />
                                    ) : (
                                        <JsonHighlight data={outputData} />
                                    )
                                ) : (
                                    <div className="text-[#555] h-full flex items-center justify-center">
                                        <div className="text-center">
                                            <Shield className="w-12 h-12 mx-auto mb-4 opacity-30" />
                                            <p className="text-sm">Les données anonymisées apparaîtront ici</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Stats and Detected Fields */}
                {detectedFields.length > 0 && (
                    <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Stats Panel */}
                        <div className="border border-[#333] bg-[#0a0a0a]">
                            <div className="border-b border-[#333] px-4 py-3">
                                <span className="font-mono text-xs uppercase tracking-wider text-[#888]">
                                    STATISTIQUES
                                </span>
                            </div>
                            <div className="p-4">
                                <div className="stats-item border-[#333]">
                                    <span className="text-[#888]">TOTAL DÉTECTÉ</span>
                                    <span className="text-[#00ff94] font-bold" data-testid="total-detected">{totalDetected}</span>
                                </div>
                                {Object.entries(stats).map(([type, count]) => (
                                    <div key={type} className="stats-item border-[#333]">
                                        <span className="text-[#888]">{FIELD_TYPE_LABELS[type] || type}</span>
                                        <span className="text-[#eee]">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Detected Fields List */}
                        <div className="lg:col-span-2 border border-[#333] bg-[#0a0a0a]">
                            <div className="border-b border-[#333] px-4 py-3">
                                <span className="font-mono text-xs uppercase tracking-wider text-[#888]">
                                    CHAMPS ANONYMISÉS
                                </span>
                            </div>
                            <div className="p-4 max-h-[300px] overflow-auto">
                                {detectedFields.map((field, index) => (
                                    <div key={index} className="field-item bg-[#0f0f0f]" data-testid={`field-item-${index}`}>
                                        <div className="flex-1">
                                            <div className="field-path">{field.path}</div>
                                            <div className="flex items-center gap-4 mt-1">
                                                <span className="text-[#ff3333] text-[10px] line-through opacity-70">
                                                    {field.original}
                                                </span>
                                                <span className="text-[#888]">→</span>
                                                <span className="text-[#00ff94] text-[10px]">
                                                    {field.anonymized}
                                                </span>
                                            </div>
                                        </div>
                                        <span className="field-type px-2 py-1 bg-[#00ff94]/10 border border-[#00ff94]/30">
                                            {FIELD_TYPE_LABELS[field.type] || field.type}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Footer Info */}
                <footer className="mt-8 border-t border-[#333] pt-6">
                    <div className="font-mono text-[10px] text-[#555] uppercase tracking-wider">
                        <p className="mb-2">TYPES DE DONNÉES DÉTECTÉES AUTOMATIQUEMENT:</p>
                        <div className="flex flex-wrap gap-2">
                            {Object.values(FIELD_TYPE_LABELS).map((label) => (
                                <span key={label} className="px-2 py-1 border border-[#333] bg-[#0a0a0a]">
                                    {label}
                                </span>
                            ))}
                        </div>
                    </div>
                </footer>
            </main>
        </div>
    );
}

export default App;
