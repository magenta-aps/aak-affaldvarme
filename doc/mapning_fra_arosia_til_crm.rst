MAPNING FRA AROSIA TIL CRM
==========================

Aktør/Bruger/Kunde
------------------
Aktør findes i AROSia i tabellen dbo.Contact

Person og virksomhed mappes til hhv. Bruger og Organisation i LoRa

Tabellen indeholder både kunder og virksomheder, hvor felterne ava_CPRnummer og
ava_CVRnummer indeholder henholdsvist CPR- og CVR-numre.

Navn og adresse hentes fra Serviceplatformen ud fra opslag på CPR eller CVR.
Følgende felter er fælles for både person og virksomhed:

=======================     =======================     =======================
CRM                         Arosia                      LoRa
=======================     =======================     =======================
Telefon                     MobilePhone / Telephone1    adresser
                                                        (urn:arosia_tel:x)
E-mail                      EMailAdress1                adresser
                                                        (urn:arosia_email:x)
Modtag SMS notif.           ava_sms_notifikation        ava_sms_notifikation
AROSia ID                   ContactId                   adresser
                                                        (urn:arosia_id:x)


For personer gælder følgende mapning:
Adresse slås op i DAWA og DAWA-UUID gemmes som adresse-relation
=======================     =======================     =======================
CRM                         Arosia                      LoRa
=======================     =======================     =======================
CPR-nummer                  ava_CPRnummer               tilknyttedepersoner
Firstname                   <CPR>                       ava_fornavn
Middlename                  <CPR>                       ava_mellemnavn
Lastname                    <CPR>                       ava_efternavn
Koen                        <CPR>                       ava_koen
Civilstand                  <CPR>                       ava_civilstand
Navn og adressebesk.        <CPR>                       ava_adressebeskyttelse


For virksomheder gælder følgende mapning:
CVR-register har indeholder allerede DAWA-UUID så her er et opslag til DAWA
ikke nødvendigt.
=======================     =======================     =======================
CRM                         Arosia                      LoRa
=======================     =======================     =======================
CVR-nummer                  ava_CVRnummer               virksomhed
Navn                        <CVR>                       organisationsnavn
Kreditstatus                ?                           N/A⁺
P-nummer                    ava_pnummer⁺⁺               N/A⁺
Virksomhedsform             <CVR>                       virksomhedstype
Branchekode                 <CVR>                       branche
Adresse-UUID                <CVR>                       adresse

⁺ Indsættes ikke i CRM
⁺⁺ P-nummer findes som felt i AROSia men feltet er altid tomt

Kunderolle
----------
Kunderolle findes i AROSia i tabellen dbo.ava_kontaktrolle
Kunderolle mappes til OrganisationFunktion i LoRa

Kunderoller i AROSia har ikke noget navn. Derfor laves navnet som en
kombination af rolle og kontakt.

Kunderoller i AROSia har intet navn, så navnet er en konkatenering af rollen
(ava_Rolle) og kontaktens navn (ava_KontaktName).

=======================     =======================     =======================
CRM                         Arosia                      LoRa
=======================     =======================     =======================
Navn                        ava_KontaktName             brugervendtnoegle ⁺⁺⁺
Aktør                       ava_Kontakt ⁺               tilknyttedebrugere
Kundeforhold                ava_Kundeforhold ⁺⁺         tilknyttedif
Rolle                       ava_Rolle                   funktionsnavn


⁺ Reference til aktør
⁺⁺ Reference til kundeforhold
⁺⁺⁺ Nøglen er sammensat af rolle og kontaktnavn


Kundeforhold
------------
Kundeforhold findes i AROSia i tabellen dbo.Account
Kundeforhold mappes til Interessefælleskab i LoRa

Forkortelserne 'ifnavn' og 'iftype' refererer til hhv.
'interessefælleskabsnavn' og 'interessefællesskabstype'

=======================     =======================     =======================
CRM                         Arosia                      LoRa
=======================     =======================     =======================
Kundeforhold                Name                        ifnavn
Kundenummer                 AccountNumber               brugervendtnoegle
Kundetype                   "AFFALD"                    iftype
Kundeforholdstype           <Udfyldes Ikke>             -
Ejendom                     <TBD>                       -


Aftale
------
Aftale findes i AROSia i tabellen dbo.ava_kundeaftale
Aftale mappes til Indsats i LoRa

Aftaler i Arosia har ikke noget unikt navn, så brugervendtnoegle sammensættes af
navn (ava_navn) og faktureringsadresse (ava_Kundeforholdname)

=======================     =======================     =======================
CRM                         Arosia                      LoRa
=======================     =======================     =======================
Navn                        ava_navn                    brugervendtnoegle⁺⁺⁺⁺
Kundeforhold                ava_kundeforhold⁺           indsatsmodtager
Aftaletype                  "AFFALD"                    indsatstype
Beskrivelse                 <Udfyldes ikke>             -
Produkter                   <Refs til Klasse>⁺⁺⁺        indsatskvalitet
Antal produkter             n/a⁺⁺                       beskrivelse
Faktureringsadresse         ava_Kundeforholdname        indsatsdokument
Ejendom                     <TBD>                       -
Startdato                   ava_Startdato               starttidspunkt
Slutdato                    ava_Slutdato                sluttidspunkt

⁺ Reference til kundeforhold
⁺⁺ Antal referencer fra produkt til aftale
⁺⁺⁺ Indeholder referencer til produkter fra ava_placeretmateriel, indsat i
LoRa som Klasse
⁺⁺⁺⁺ Nøglen er sammensat af navn og faktureringsadresse


Produkt
-------
Produkt findes i AROSia i tabellen dbo.ava_placeretmateriel
Produkt mappes til Klasse i LoRa

=======================     =======================     =======================
CRM                         Arosia                      LoRa
=======================     =======================     =======================
Navn                        ava_navn                    titel
Identifikation              ava_stregkode               brugervendtnoegle
Aftale                      <Redundant>                 (findes på aftale/indsats)
Adresse                     <Redundant>                 (findes på aftale/indsats)
Installationstype           "AFFALD"                    overordnet_klasse
Afhentningstype             ava_affaldstypeName         ava_afhentningstype
Beskrivelse                 <Udfyldes ikke>             -
Kundenummer                 <Redundant>                 (findes på kundeforhold)
AROSia id                   ava_placeretmaterielId      ava_arosia_id


Sag
---

<TBC>
Indsættes ikke i første omgang

Sag findes i AROSia i tabellen dbo.Incident
Sag mapperes til Sag i LoRa

=======================     =======================     =======================
CRM                         Arosia                      LoRa
=======================     =======================     =======================
Aktør                       CustomerId                  primaerpart?
Emne                        SubjectId                   ? - custom field?
Sagstitel                   Title                       titel
Id                          TicketNumber                sagsnummer
Oprindelse                  CaseOriginCode              ? - custom field
Beskrivelse                 Description                 beskrivelse
Adresse                     ?                           ? - Opslag i DAWA
Kundeforhold                AccountId                   ? - ref til kundeforhold
Produkt                     ?                           ? - ref til produkt

Henvendelsesadresse         ?                           ? - custom fields?
By (H)                      ?                           ? - custom fields?
Email (H)                   ?                           ? - custom fields?
Instnr. (H)                 ?                           ? - custom fields?
Henv.kilde (H)              ?                           ? - custom fields?
Kommentar (H)               ?                           ? - custom fields?
Kundenummer (H)             ?                           ? - custom fields?
Navn (H)                    ?                           ? - custom fields?
Postnummer (H)              ?                           ? - custom fields?
Telefon (H)                 ?                           ? - custom fields?
Henvendelse vedr. (H)       ?                           ? - custom fields?
=======================     =======================     =======================

