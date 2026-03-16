"""
Module d'anonymisation de données JSON
Détection automatique et remplacement des données sensibles françaises
"""
import re
import random
import string
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass

# Données françaises fictives
PRENOMS_MASCULINS = [
    "Jean", "Pierre", "Paul", "Jacques", "Michel", "André", "Philippe", "Alain",
    "Bernard", "Claude", "François", "Olivier", "Thierry", "Nicolas", "Christophe",
    "Sébastien", "Julien", "Thomas", "Alexandre", "Maxime", "Antoine", "Lucas",
    "Hugo", "Louis", "Nathan", "Mathis", "Léo", "Gabriel", "Raphaël", "Arthur"
]

PRENOMS_FEMININS = [
    "Marie", "Jeanne", "Françoise", "Monique", "Nicole", "Catherine", "Isabelle",
    "Nathalie", "Sophie", "Sandrine", "Valérie", "Sylvie", "Christine", "Martine",
    "Anne", "Julie", "Camille", "Emma", "Léa", "Chloé", "Manon", "Sarah", "Clara",
    "Zoé", "Louise", "Alice", "Lina", "Rose", "Jade", "Lucie"
]

NOMS = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois",
    "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David",
    "Bertrand", "Morel", "Fournier", "Girard", "Bonnet", "Dupont", "Lambert", "Fontaine",
    "Rousseau", "Vincent", "Muller", "Lefevre", "Faure", "Andre", "Mercier", "Blanc",
    "Guerin", "Boyer", "Garnier", "Chevalier", "Francois", "Legrand", "Gauthier", "Garcia"
]

RUES = [
    "rue de la Paix", "rue du Commerce", "avenue des Champs-Élysées", "boulevard Voltaire",
    "rue Victor Hugo", "avenue de la République", "rue Jean Jaurès", "rue Pasteur",
    "rue de la Liberté", "avenue du Général de Gaulle", "rue Nationale", "rue du Moulin",
    "rue des Fleurs", "avenue Foch", "boulevard Saint-Michel", "rue de Paris",
    "rue du Château", "avenue Gambetta", "rue de la Gare", "rue des Lilas"
]

VILLES = [
    ("Paris", "75001"), ("Lyon", "69001"), ("Marseille", "13001"), ("Toulouse", "31000"),
    ("Nice", "06000"), ("Nantes", "44000"), ("Strasbourg", "67000"), ("Montpellier", "34000"),
    ("Bordeaux", "33000"), ("Lille", "59000"), ("Rennes", "35000"), ("Reims", "51100"),
    ("Le Havre", "76600"), ("Saint-Étienne", "42000"), ("Toulon", "83000"), ("Grenoble", "38000"),
    ("Dijon", "21000"), ("Angers", "49000"), ("Nîmes", "30000"), ("Villeurbanne", "69100")
]

DOMAINES_EMAIL = [
    "gmail.com", "yahoo.fr", "orange.fr", "free.fr", "sfr.fr", "outlook.fr",
    "hotmail.fr", "laposte.net", "wanadoo.fr", "bbox.fr"
]

# Patterns de détection
FIELD_PATTERNS = {
    "nom": [
        r"^nom$", r"^name$", r"^lastname$", r"^last_name$", r"^family_name$",
        r"^nom_famille$", r"^surname$", r"nom_de_famille", r"family"
    ],
    "prenom": [
        r"^prenom$", r"^prénom$", r"^firstname$", r"^first_name$", r"^given_name$",
        r"^givenname$", r"prenom", r"prénom"
    ],
    "nom_complet": [
        r"^fullname$", r"^full_name$", r"^nom_complet$", r"^complete_name$",
        r"^displayname$", r"^display_name$"
    ],
    "email": [
        r"^email$", r"^e-mail$", r"^mail$", r"^courriel$", r"^adresse_email$",
        r"^email_address$", r"^emailaddress$"
    ],
    "telephone": [
        r"^tel$", r"^telephone$", r"^téléphone$", r"^phone$", r"^phone_number$",
        r"^phonenumber$", r"^mobile$", r"^portable$", r"^numero_tel$", r"^num_tel$",
        r"^fax$", r"^cellphone$"
    ],
    "adresse": [
        r"^adresse$", r"^address$", r"^rue$", r"^street$", r"^street_address$",
        r"^adresse_postale$", r"^postal_address$", r"^voie$", r"^ligne_adresse$"
    ],
    "code_postal": [
        r"^code_postal$", r"^codepostal$", r"^postal_code$", r"^postalcode$",
        r"^zip$", r"^zipcode$", r"^zip_code$", r"^cp$"
    ],
    "ville": [
        r"^ville$", r"^city$", r"^commune$", r"^localite$", r"^town$"
    ],
    "iban": [
        r"^iban$", r"^bank_account$", r"^compte_bancaire$", r"^numero_compte$",
        r"^account_number$"
    ],
    "secu": [
        r"^nir$", r"^secu$", r"^securite_sociale$", r"^social_security$",
        r"^numero_secu$", r"^num_secu$", r"^ssn$", r"^nss$", r"^numero_securite_sociale$"
    ],
    "date_naissance": [
        r"^date_naissance$", r"^datenaissance$", r"^birth_date$", r"^birthdate$",
        r"^dob$", r"^date_of_birth$", r"^naissance$"
    ],
    "carte_bancaire": [
        r"^carte$", r"^card$", r"^credit_card$", r"^carte_bancaire$",
        r"^card_number$", r"^numero_carte$"
    ]
}

# Patterns de valeurs pour détection automatique
VALUE_PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "telephone_fr": r"^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$",
    "iban_fr": r"^FR\d{2}\s*(?:\d{4}\s*){5}\d{3}$",
    "secu_fr": r"^[12]\s*\d{2}\s*(?:0[1-9]|1[0-2]|2[0-9]|[3-9][0-9])\s*\d{2}\s*\d{3}\s*\d{3}\s*\d{2}$",
    "code_postal_fr": r"^\d{5}$",
    "date_fr": r"^\d{2}/\d{2}/\d{4}$",
    "carte_bancaire": r"^\d{4}\s*\d{4}\s*\d{4}\s*\d{4}$"
}


@dataclass
class DetectedField:
    """Représente un champ détecté comme sensible"""
    path: str
    field_type: str
    original_value: Any
    anonymized_value: Any


class JSONAnonymizer:
    """Classe principale pour l'anonymisation de JSON"""
    
    def __init__(self):
        self.detected_fields: List[DetectedField] = []
        self.name_mapping: Dict[str, str] = {}  # Pour cohérence des noms dans le document
        
    def generate_prenom(self) -> str:
        """Génère un prénom français aléatoire"""
        all_prenoms = PRENOMS_MASCULINS + PRENOMS_FEMININS
        return random.choice(all_prenoms)
    
    def generate_nom(self) -> str:
        """Génère un nom de famille français aléatoire"""
        return random.choice(NOMS)
    
    def generate_nom_complet(self) -> str:
        """Génère un nom complet français"""
        return f"{self.generate_prenom()} {self.generate_nom()}"
    
    def generate_email(self, prenom: str = None, nom: str = None) -> str:
        """Génère un email français fictif"""
        if not prenom:
            prenom = self.generate_prenom()
        if not nom:
            nom = self.generate_nom()
        
        prenom_clean = prenom.lower().replace("é", "e").replace("è", "e").replace("ë", "e")
        nom_clean = nom.lower().replace("é", "e").replace("è", "e").replace("ë", "e")
        
        formats = [
            f"{prenom_clean}.{nom_clean}",
            f"{prenom_clean}{nom_clean}",
            f"{prenom_clean[0]}.{nom_clean}",
            f"{prenom_clean}_{nom_clean}",
            f"{nom_clean}.{prenom_clean}"
        ]
        
        email_base = random.choice(formats)
        if random.random() > 0.5:
            email_base += str(random.randint(1, 99))
        
        domain = random.choice(DOMAINES_EMAIL)
        return f"{email_base}@{domain}"
    
    def generate_telephone(self) -> str:
        """Génère un numéro de téléphone français fictif"""
        prefixes = ["06", "07", "01", "02", "03", "04", "05", "09"]
        prefix = random.choice(prefixes)
        
        numbers = [str(random.randint(10, 99)) for _ in range(4)]
        
        formats = [
            f"{prefix} {' '.join(numbers)}",
            f"{prefix}.{'.'.join(numbers)}",
            f"{prefix}{numbers[0]}{numbers[1]}{numbers[2]}{numbers[3]}",
            f"+33 {prefix[1]} {' '.join(numbers)}"
        ]
        
        return random.choice(formats)
    
    def generate_adresse(self) -> str:
        """Génère une adresse française fictive"""
        numero = random.randint(1, 150)
        rue = random.choice(RUES)
        return f"{numero} {rue}"
    
    def generate_code_postal(self) -> str:
        """Génère un code postal français"""
        ville, cp = random.choice(VILLES)
        return cp
    
    def generate_ville(self) -> str:
        """Génère une ville française"""
        ville, cp = random.choice(VILLES)
        return ville
    
    def generate_adresse_complete(self) -> str:
        """Génère une adresse complète"""
        numero = random.randint(1, 150)
        rue = random.choice(RUES)
        ville, cp = random.choice(VILLES)
        return f"{numero} {rue}, {cp} {ville}"
    
    def generate_iban(self) -> str:
        """Génère un IBAN français fictif"""
        # Format: FRkk BBBB BGGG GGCC CCCC CCCC CKK
        bank_code = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        branch_code = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        account = ''.join([str(random.randint(0, 9)) for _ in range(11)])
        key = ''.join([str(random.randint(0, 9)) for _ in range(2)])
        check = ''.join([str(random.randint(0, 9)) for _ in range(2)])
        
        return f"FR{check} {bank_code} {branch_code} {account[:4]} {account[4:8]} {account[8:]}X {key}"
    
    def generate_secu(self) -> str:
        """Génère un numéro de sécurité sociale français fictif"""
        # Format: S AA MM DD CCC OOO KK
        sexe = random.choice(["1", "2"])
        annee = str(random.randint(50, 99))
        mois = str(random.randint(1, 12)).zfill(2)
        dept = str(random.randint(1, 95)).zfill(2)
        commune = str(random.randint(1, 999)).zfill(3)
        ordre = str(random.randint(1, 999)).zfill(3)
        cle = str(random.randint(1, 97)).zfill(2)
        
        return f"{sexe} {annee} {mois} {dept} {commune} {ordre} {cle}"
    
    def generate_date_naissance(self) -> str:
        """Génère une date de naissance fictive"""
        jour = str(random.randint(1, 28)).zfill(2)
        mois = str(random.randint(1, 12)).zfill(2)
        annee = str(random.randint(1950, 2005))
        return f"{jour}/{mois}/{annee}"
    
    def generate_carte_bancaire(self) -> str:
        """Génère un numéro de carte bancaire fictif"""
        groups = [''.join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(4)]
        return ' '.join(groups)
    
    def detect_field_type(self, key: str, value: Any) -> str | None:
        """Détecte le type de champ sensible"""
        key_lower = key.lower().strip()
        
        # Vérification par nom de champ
        for field_type, patterns in FIELD_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, key_lower, re.IGNORECASE):
                    return field_type
        
        # Vérification par valeur si c'est une chaîne
        if isinstance(value, str):
            value_clean = value.strip()
            
            # Email
            if re.match(VALUE_PATTERNS["email"], value_clean):
                return "email"
            
            # Téléphone français
            if re.match(VALUE_PATTERNS["telephone_fr"], value_clean.replace(" ", "").replace(".", "").replace("-", "")):
                return "telephone"
            
            # IBAN
            if re.match(VALUE_PATTERNS["iban_fr"], value_clean.replace(" ", ""), re.IGNORECASE):
                return "iban"
            
            # Numéro de sécurité sociale
            if re.match(VALUE_PATTERNS["secu_fr"], value_clean.replace(" ", "")):
                return "secu"
            
            # Code postal (seulement si le nom suggère aussi)
            if re.match(VALUE_PATTERNS["code_postal_fr"], value_clean):
                if any(kw in key_lower for kw in ["code", "postal", "zip", "cp"]):
                    return "code_postal"
            
            # Date de naissance
            if re.match(VALUE_PATTERNS["date_fr"], value_clean):
                if any(kw in key_lower for kw in ["date", "naissance", "birth", "dob"]):
                    return "date_naissance"
            
            # Carte bancaire
            if re.match(VALUE_PATTERNS["carte_bancaire"], value_clean.replace(" ", "").replace("-", "")):
                return "carte_bancaire"
        
        return None
    
    def anonymize_value(self, field_type: str) -> Any:
        """Génère une valeur anonymisée selon le type"""
        generators = {
            "nom": self.generate_nom,
            "prenom": self.generate_prenom,
            "nom_complet": self.generate_nom_complet,
            "email": self.generate_email,
            "telephone": self.generate_telephone,
            "adresse": self.generate_adresse,
            "code_postal": self.generate_code_postal,
            "ville": self.generate_ville,
            "iban": self.generate_iban,
            "secu": self.generate_secu,
            "date_naissance": self.generate_date_naissance,
            "carte_bancaire": self.generate_carte_bancaire
        }
        
        generator = generators.get(field_type)
        if generator:
            return generator()
        return None
    
    def anonymize_recursive(self, data: Any, path: str = "") -> Any:
        """Anonymise récursivement une structure JSON"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Détecter le type de champ
                field_type = self.detect_field_type(key, value)
                
                if field_type and not isinstance(value, (dict, list)):
                    # Anonymiser la valeur
                    anonymized = self.anonymize_value(field_type)
                    if anonymized:
                        self.detected_fields.append(DetectedField(
                            path=current_path,
                            field_type=field_type,
                            original_value=value,
                            anonymized_value=anonymized
                        ))
                        result[key] = anonymized
                    else:
                        result[key] = value
                else:
                    # Continuer la récursion
                    result[key] = self.anonymize_recursive(value, current_path)
            return result
        
        elif isinstance(data, list):
            return [
                self.anonymize_recursive(item, f"{path}[{i}]")
                for i, item in enumerate(data)
            ]
        
        else:
            return data
    
    def anonymize(self, data: Any) -> Tuple[Any, List[Dict]]:
        """
        Point d'entrée principal pour l'anonymisation
        
        Args:
            data: Données JSON à anonymiser
            
        Returns:
            Tuple contenant:
            - Les données anonymisées
            - La liste des champs détectés et modifiés
        """
        self.detected_fields = []
        self.name_mapping = {}
        
        anonymized_data = self.anonymize_recursive(data)
        
        detected_summary = [
            {
                "path": f.path,
                "type": f.field_type,
                "original": str(f.original_value)[:50] + ("..." if len(str(f.original_value)) > 50 else ""),
                "anonymized": str(f.anonymized_value)
            }
            for f in self.detected_fields
        ]
        
        return anonymized_data, detected_summary


def anonymize_json(data: Any) -> Tuple[Any, List[Dict]]:
    """Fonction utilitaire pour anonymiser un JSON"""
    anonymizer = JSONAnonymizer()
    return anonymizer.anonymize(data)
