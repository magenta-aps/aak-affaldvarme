
KMD EE Notifications - data to watch out for
============================================

In order to implement notifications from KMD EE, we need to find out if
data that we care for have changed on objects that we care for - so to
speak. 

"Objects that we care for" are objects that have been exported to the
CRM system. "Data that we care for" are fields that we actually write.

We use data from the following KMD EE tables:

* Kunde
* Forbrugssted
* TrefInstallation
* TrefMaaler
* AlternativSted

From the respective tables, we use the following fields:

Kunde
=====

PersonnrSEnr
LigestPersonnr
Kundenr
KundeSagsnr
KundeNavn
Telefonnr
EmailKunde
MobilTlf
ForbrugsstedID
VejNavn
Postdistrikt
Tilflytningsdato
Fraflytningsdato
KundeID

Forbrugssted
============

ForbrStVejnavn
Vejkode
Postnr
Postdistrikt
Husnr
Bogstav
Etage
Sidedørnr


TrefInstallation
================

InstalNummer
AlternativStedID
InstallationID


TrefMaaler
==========

Målernr
MaalerTypeBetegnel
Målertypefabrikat
DatoFra
DatoTil
InstallationID



AlternativSted
==============

ForbrStVejnavn
VejkodeAltern
Postnr
HusnrAltern
Bogstav
EtageAltAdr
SidedørnrAltern
