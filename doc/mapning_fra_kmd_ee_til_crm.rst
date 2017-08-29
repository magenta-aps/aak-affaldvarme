
MAPNING FRA KMD EE TIL CRM
==========================

Aktør/Bruger/Kunde
------------------

Navn og folkeregisteradresse hentes af KMD-agenten ved opslag ud fra
CPR-nummer eller CVR-nummer fra feltet KundeCPRNr for privatkunder.

Den eksakte arkitektur af denne løsning er endnu ikke fastlagt. En
mulighed er, at KMD EE-agenten (Mox KMD EE) ved ændringer i
CPR-oplysninger sender en notifikation (via AMQP) til SP-agenten (Mox
SP), som vil sørge for at opdatere oplysningerne i LoRa. På denne måde
vil Mox KMD EE aldrig skulle opdatere oplysninger, der vedligeholdes
med data fra Serviceplatformen.

Det samme gælder for CVR-oplysninger.

En model
kunne være, at Mox KMD EE
CPR- og CVR-numrene ligger begge i feltet KundeCprNr og kan kendes fra
hinanden ved at CPR-numre er ti-cifrede, hvor CVR-numre er otte-cifrede. 

Telefon og email gemmes som adresser jfr objektrepræsentationsdokumentet
og hentes fra felterne EmailKunde, Telefon og  MobilTlf i KMD EE.

Mapningen af CRM-systemets *aktør* bliver dermed som angivet i tabellen
herunder.

=======================     =======================  
CRM                         KMD EE
=======================     =======================  
CPR-nummer                  PersonnrSEnr
<CPR-oplysninger>           (Mox SP)
CVR-nummer                  PersonnrSEnr
<CVR-oplysninger>           (Mox CVR)
Telefon KMD EE              Telefon
E-mail KMD EE               EmailKunde
MobilTlf⁺                   MobilTlf
Fax⁺                        Fax
=======================     =======================  

Det vil sige, at det kun er kontaktoplysningerne, som faktisk kopieres
fra Kunde-tabellen i KMD EE til Aktøren i CRM-systemet.

⁺ Felterne MobilTlf og Fax eksisterer p.t. ikke i CRM-systemet, men kan
godt blive relevante - om ikke andet kan MobilTlf sandsynligvis. Det er
aftalt med AVA, at de overføres til LoRa for det tilfældes skyld, at de
senere skal føjes til CRM-systemet.


Kunderolle
----------

Kunderollens navn sammensættes af kundens adresse (vej + husnummer +
postnummer + etage) samt rolleværdien. Dette blot for at få noget unikt. 

Kunderollen har to relationer, nemlig til Aktør og Kundeforhold, der
derfor skal oprettes samtidig med rollen. En anden måde at sige dette på
er, at kunderollen ikke har nogen mening som selvstændigt objekt, den er
alene et bindeled mellem kunden og kundeforholdet.

De kunder, der er opført i kunderecords i KMD EE, og hvis person- eller
CVR-nummer er angivet i 

TODO: **AFVENTER AFKLARING FRA AVA**


Kundeforhold
------------

Mapppes som angivet i tabellen herunder.


=======================     =======================  
CRM                         KMD EE
=======================     =======================  
Kundeforhold                Vejnavn, Postdistrikt
Kundenummer                 Kundenr
Kundetype                   <Altid Varme>
Kundeforholdstype           <Udfyldes ikke>
=======================     =======================  


Aftale
------

Mappes som angivet i tabellen herunder.


=======================     =======================
CRM                         KMD EE
=======================     =======================
Navn                        <aftales med AVA>
Kundeforhold                <Relation til 
                              Kundeforhold>
Aftaletype                  <Altid Varme>
Beskrivelse                 <Udfyldes ikke>
Antal produkter             <Redundant?>
Faktureringsadresse         <Der er ikke nogen på 
                              Forbrugssted - skal
                              den udfyldes?>
Adresse                     Forbrugssted.Adresse
Ejendom                     Forbrugssted.Ejendomsnr
=======================     =======================


Produkt
-------

Mappes som angivet i tabellen herunder.


=======================     =======================
CRM                         KMD EE
=======================     =======================
Navn                        <?>
Identifikation              Trefinstallation.
                              InstalNummer
Aftale                      <Relation til Aftale>
Adresse                     <Redundant = 
                             Forbrugssted.Adresse>
Installationstype           <Altid Varme>
Afhentningstype             <Udfyldes ikke>
Målernummer                 TrefMaaler.Målernr
Beskrivelse                 
Kundenummer                 <Redundant>
=======================     =======================
