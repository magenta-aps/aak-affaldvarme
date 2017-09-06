
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

Kunderollens navn er blot rolleværdien - dette for at det kan blive så
informativt som muligt i brugerinterfacet.

Kunderollen har to relationer, nemlig til Aktør og Kundeforhold, der
derfor skal oprettes samtidig med rollen. En anden måde at sige dette på
er, at kunderollen ikke har nogen mening som selvstændigt objekt, den er
alene et bindeled mellem kunden og kundeforholdet.

* De kunder, der er opført i Kunde-tabellen i KMD EE, og hvis person-
  eller CVR-nummer er angivet i feltet ``PersonnrSEnr``, tildeles rollen
  "Kunde".  
  
* De personer, hvis personnummer er angivet i
  Kunde-tabellens ``LigestPersonnr``, oprettes og tildeles rollen
  "Ligestillingskunde".

* De personer, der er angivet som FasAdministrator i feltet
  ``Kunde.FasadministratorID`` oprettes og tildeles rollen
  "Administrator". Bemærk, at disse ikke har ``PersonnrSEnr`` udfyldt,
  men de har ofte et CPR- eller CVR-nummer i feltet ``BemærkAdmin``.

* De personer, der er angivet med ``Forbrugssted.ViceværtID``, oprettes
  og tildeles rollen "Vicevært". 
  

Bemærk, at vicevært-tabellen er *tom* i de databasedumps for KMD EE, som
vi har adgang til, så den er måske ikke relevant.




Kundeforhold
------------

Mapppes som angivet i tabellen herunder.


=======================     =======================  
CRM                         KMD EE
=======================     =======================  
Kundeforhold                <Varme + kundens adresse som i LoRa/CRM>
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
                             den udfyldes? Hvor kommer
                             den fra?>
Adresse                     Forbrugssted.Adresse
Ejendom                     Forbrugssted.Ejendomsnr⁺
=======================     =======================

⁺: Ejendommen slås op i BBR og de relevante oplysninger overføres til
CRM af CRM-agenten.


Produkt
-------

Mappes som angivet i tabellen herunder.


=======================     =======================
CRM                         KMD EE
=======================     =======================
Navn                        TrefMaaler.Målertypefab
                            rikat + TrefMaaler.Maale
                            rTypeBetegnel 
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
