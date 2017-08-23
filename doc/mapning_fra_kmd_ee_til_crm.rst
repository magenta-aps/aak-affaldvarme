
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
CPR-nummer                  KundeCprNr
<CPR-oplysninger>           (Mox SP)
CVR-nummer                  KundeCprNr
<CVR-oplysninger>           (Mox CVR)
Telefon KMD EE              Telefon
E-mail KMD EE               EmailKunde
=======================     =======================  

Det vil sige, at det kun er kontaktoplysningerne, som faktisk kopieres
fra Kunde-tabellen i KMD EE til Aktøren i CRM-systemet.


Kunderolle
----------

Kunderollens navn sammensættes af kundens adresse (vej + husnummer +
postnummer + etage) samt rolleværdien. Dette blot for at få noget unikt. 

Kunderollen har to relationer, nemlig til Aktør og Kundeforhold, der
derfor skal oprettes samtidig med rollen. En anden måde at sige dette på
er, at kunderollen ikke har nogen mening som selvstændigt objekt, den er
alene et bindeled mellem kunden og kundeforholdet.

Den eneste reelle oplysning fra KMD EE i dette objekt er derfor selve
rollen. Den stammer ikke fra et enkelt felt, men udledes således:

* Hvis feltet ```Kunde.LigestPersonnr``` er udfyldt, er rollen
  "Ligestillingsejer".

* Hvis feltet ```Kunde.Perso
