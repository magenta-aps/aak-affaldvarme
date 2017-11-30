
MAPNING FRA KMD EE TIL CRM
==========================

Aktør/Bruger/Kunde
------------------

Navn og folkeregisteradresse hentes af KMD-agenten ved opslag ud fra
CPR-nummer eller CVR-nummer fra feltet KundeCPRNr for privatkunder.

Disse oplysninger lægges ved oprettelse af nye kunder i LoRa sammen med
oplysningerne fra KMD EE. Opdatering af oplysningerne i
Serviceplatformen vil derimod blive håndteret af Mox SP-agenten.

CPR- og CVR-numrene ligger begge i feltet KundeCprNr eller PersonnrSEnr
(de to felter har samme indhold) og kan kendes fra hinanden ved at
CPR-numre er ni- eller ti-cifrede, hvor CVR-numre er otte-cifrede. 

Telefon og email gemmes som adresser jfr objektrepræsentationsdokumentet
og hentes fra felterne EmailKunde, Telefon og  MobilTlf i KMD EE.

Mapningen af CRM-systemets *aktør* bliver dermed som angivet i tabellen
herunder.



=======================     =======================    =================       
CRM                         KMD EE                     LoRa
=======================     =======================    =================       
CPR-nummer                  PersonnrSEnr               tilknyttede-
                                                       personer
<CPR-oplysninger>           (Mox SP)
CVR-nummer                  PersonnrSEnr               virksomhed
<CVR-oplysninger>           (Mox CVR)
Telefon KMD EE              Telefon                    adresser
E-mail KMD EE                 
MobilTlf⁺                   MobilTlf                   adresser
Fax⁺                        Fax                        overføres ikke
MasterID                    KundeSagsnr                ava_masterid
=======================     =======================    =================         


⁺ Felterne MobilTlf og Fax eksisterer p.t. ikke i CRM-systemet, men kan
godt blive relevante - om ikke andet kan MobilTlf sandsynligvis. Det er
aftalt med AVA, at de overføres til LoRa for det tilfældes skyld, at de
senere skal føjes til CRM-systemet.

Det vil sige, at det kun er kontaktoplysningerne, som faktisk kopieres
fra Kunde-tabellen i KMD EE til Aktøren i CRM-systemet.

Personoplysningerne fra Serviceplatformen repræsenteres ved lokale
udvidelser til objektet Bruger. 

Disse oplysninger er som følger:

=============    ================
Person (CPR)     LoRa
=============    ================
Fornavn          ava_fornavn
Mellemnavn       ava_mellemnavn
Efternavn        ava_efternavn
Civilstand       ava_civilstand
Køn              ava_koen
Adresse-         ava_adresse-
beskyttelse      beskyttelse
=============    ================

Derudover hentes borgerens *adresse* fra Serviceplatformen og slås op i
DAWA, hvorefter addresse-UUID'en gemmes i brugerens relation "adresser"
ligesom email og telefonnummer.

For virksomheder hentes, som det fremgår af tabellen herunder,
virksomhedens navn, adresse-UUID (CVR-registret på Serviceplatformen
indeholder DAWA-UUID, så det er ikke nødvendigt at slå op),
virksomhedsform og branchekode.

================     =================  
Virksomhed (CVR)     LoRa
================     =================
Navn                 organisationsnavn
Adresse-UUID         adresse
Virksomhedsform      virksomhedstype
Branchekode          branche
================     =================


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
vi har adgang til, så den er formentlig ikke relevant.

Med denned definition bliver kunderollens 

* *Navn* lig med tekstrepræsentationen af rollen, f.eks. "Kunde"
* *Kundeforhold* et opslag til det relevante Kundeforhold
* *Rolle* en relation til klassifikation angivet som URN, altså f.eks.
  ``915.240.000``.
* Den numeriske nøgle bruges også som brugervendt nøgle for objektet.

Mapningen bliver hermed: 

=======================    =================     
CRM                        LoRa
=======================    =================     
Navn                       funktionsnavn
Aktør                      tilknyttedebrugere
Kundeforhold               tilknyttedeinte-
                           ressefællesskaber
Rolle                      brugervendtnoegle
=======================    =================       

Kundeforhold
------------

Mapppes som angivet i tabellen herunder.

Repræsenteres i LoRa af klassen Interessefællesskab. I tabellen herunder
repræsenterer forkortelsen "ifnavn" det rigtige, som er
"interessefaellesskabsnavn".


=======================    =======================    =================     
CRM                        KMD EE                     LoRa
=======================    =======================    =================     
Kundeforhold               <Varme + forbrugsadres-    ifnavn
                           se som i LoRa/CRM>
Kundenummer                Kundenr                    brugervendtnoegle
Kundetype                  Varme                      iftype
Kundeforholdstype          <Udfyldes ikke>
Adresse                    Forbrugssted.Adresse       adresser
=======================    =======================    =================       

Feltet "Kundeforhold" er det felt, der på de fleste andre elementer
hedder Navn. Adressen i dette navnefelt forstås som kundens
forbrugsstedets adresse, altså Forbrugssted.Adresse.


Aftale
------

Mappes som angivet i tabellen herunder.

I LoRa repræsenteres en aftale som en Indsats.

NB: For at kunne repræsentere antal produkter samt adressen burde
der - som vi allerede har set for aktørernes vedkommende - indføres en
relation og et egenskabsfelt til adressen og feltet "antal
produkter". 

Dette er imidlertid ikke muligt p.t., da klassen Indsats i LoRa er
patchet på en måde, der gør det vanskeligt at tilføje nye felter. Dette
kan der først rettes op på, når Magenta får tid til at ændre
implementationen af LoRas databaselag.



=======================     =======================    =================     
CRM                         KMD EE                     LoRa
=======================     =======================    =================
Navn                        Navn                       brugervendtnoegle
Kundeforhold                <Relation til              indsatsmodtager 
                              Kundeforhold>
Aftaletype                  Varme                      indsatstype
Beskrivelse                 <Udfyldes ikke>
Antal produkter             <Redundant>                beskrivelse⁺⁺
Produkter                   <Målere fra TrefMaaler>    indsatskvalitet
Faktureringsadresse         <DAR-adresse fundet fra    indsatsdokument⁺⁺
                            Kunde.vejnavn +
                            Kunde.postdistrikt>
Ejendom                     Forbrugsted.Ejendomsnr⁺
Startdato                   Kunde.Tilflytningsdato     starttidspunkt
Slutdato                    Kunde.fraflytningsdato     sluttidspunkt
=======================     =======================    =================

⁺: Ejendom er ikke omfattet af de OIO-standarder, som LoRa implementerer
og er i første omgang ikke med i dette projekt. I en senere fase kan de
relevante oplysninger evt. slås op i BBR og overføres til CRM af
CRM-agenten.

⁺⁺: Her er der som sagt tale om at bøje modellen, fordi det p.t. ikke er
muligt at tilføje den relevante lokale udvidelse.


Produkt
-------

Mappes som angivet i tabellen herunder.

Produkt er i LoRa repræsenteret af klassen Klasse for hierarkiet
Klassifikation.

=======================     =======================    =================
CRM                         KMD EE                     LoRa
=======================     =======================    =================
Navn                        Målernr + fabrikat +       titel
                            betegnelse (TrefInst.)
Identifikation              Trefinstallation.          brugervendtnoegle
                              InstalNummer
Aftale                      <Relation til Aftale>      (findes på
                                                       Aftale/Indsats)
Adresse                     Altern. adresse            ava_opstillingsadresse
                             eller                          
                             Forbrugssted.Adresse>
Installationstype           Varme                      overordnet_klasse
Afhentningstype             <Udfyldes ikke>
Målernummer                 TrefMaaler.Målernr         eksempel⁺
Målertype                   TrefMaaler.MaalertypeBe    beskrivelse⁺
                            tegnel
Beskrivelse                 <Udfyldes ikke>
Kundenummer                 <Redundant>                (findes på kunde-
                                                       forhold)
=======================     =======================    =================


⁺Her burde der igen have været tilføjet et nyt felt, som vi kunne have
kaldt "ava_maalernummer", men det afventer en afklaring af vores
tekniske gæld vedr. databasen.
