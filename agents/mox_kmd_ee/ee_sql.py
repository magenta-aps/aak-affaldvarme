#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""This module contains all SQL used in the KMD EE Mox Agent.

Each SQL expression used to acces the database is specified here and called
from the other modules. For instance, the variable ``CUSTOMER_SQL`` is given
below and will extract all information for relevant customer records. ::

    CUSTOMER_SQL = '''
    SELECT [PersonnrSEnr]
          ,[LigestPersonnr]
          ,[Kundenr]
          ,[KundeSagsnr]
          ,[KundeNavn]
          ,[Telefonnr]
          ,[EmailKunde]
          ,[MobilTlf]
          ,[a].[ForbrugsstedID]
          ,[VejNavn]
          ,[a].[Postdistrikt]
          ,[Tilflytningsdato]
          ,[Fraflytningsdato]
          ,[Status]
          ,[FasadministratorID]
          ,[BoligadminID]
          ,[Husnr]
          ,[ForbrStVejnavn]
          ,[Vejkode]
          ,[b].[Postdistrikt] as [ForbrStPostdistrikt]
          ,[Postnr]
          ,[Bogstav]
          ,[Etage]
          ,[Sidedørnr]
    FROM Kunde a, Forbrugssted b
    WHERE Tilflytningsdato <= GETDATE() AND Fraflytningsdato >= GETDATE()
    and Afregningsgrpnr <> 999
    and a.ForbrugsstedID = b.ForbrugsstedID
    '''

Every time a need for an SQL query is discovered, a new string (maybe
parametrized using string formatting) is created in this module.
"""

#: This is the SQL to fetch all customers from the KMD EE database.
#: Only relevant fields (please).
CUSTOMER_SQL = """
SELECT [PersonnrSEnr]
      ,[LigestPersonnr]
      ,[Kundenr]
      ,[KundeSagsnr]
      ,[KundeNavn]
      ,[Telefonnr]
      ,[EmailKunde]
      ,[MobilTlf]
      ,[a].[ForbrugsstedID]
      ,[VejNavn]
      ,[a].[Postdistrikt]
      ,[Tilflytningsdato]
      ,[Fraflytningsdato]
      ,[Status]
      ,[FasadministratorID]
      ,[BoligadminID]
      ,[Husnr]
      ,[ForbrStVejnavn]
      ,[Vejkode]
      ,[b].[Postdistrikt] as [ForbrStPostdistrikt]
      ,[Postnr]
      ,[Bogstav]
      ,[Etage]
      ,[Sidedørnr]
  FROM Kunde a, Forbrugssted b
  WHERE Tilflytningsdato <= GETDATE() AND Fraflytningsdato >= GETDATE()
  and Afregningsgrpnr <> 999
  and a.ForbrugsstedID = b.ForbrugsstedID
"""


#: Extract all relevant installations.
RELEVANT_TREF_INSTALLATIONS_SQL = """SELECT [InstalNummer],
                                 [AlternativStedID],
                                 [Målernr],
                                 [MaalerTypeBetegnel],
                                 [Målertypefabrikat],
                                 [DatoFra],
                                 [DatoTil],
                                 [Kundenr]
    FROM TrefInstallation a, TrefMaaler b, Kunde c
    WHERE
    a.InstallationID = b.InstallationID
    AND b.DatoFra <= GETDATE() and b.DatoTil >= GETDATE()
    AND a.ForbrugsstedID = c.ForbrugsstedID
    AND c.Tilflytningsdato <= GETDATE() AND c.Fraflytningsdato >= GETDATE()
    AND a.ForbrugsstedID IN (SELECT a.ForbrugsstedID from Kunde a,
    Forbrugssted b
  WHERE Tilflytningsdato <= GETDATE() AND Fraflytningsdato >= GETDATE()
  and Afregningsgrpnr <> 999
  and a.ForbrugsstedID = b.ForbrugsstedID)
    """

#: Installation data for a given Forbrugssted.
TREFINSTALLATION_SQL = """SELECT [InstalNummer],
                                 [AlternativStedID],
                                 [Målernr],
                                 [MaalerTypeBetegnel],
                                 [Målertypefabrikat],
                                 [DatoFra],
                                 [DatoTil]
    FROM TrefInstallation a, TrefMaaler b
    WHERE ForbrugsstedID = {0}
    AND a.InstallationID = b.InstallationID
    AND b.DatoFra <= GETDATE() and b.DatoTil >= GETDATE()
    """

#: Alternative address for a given Alt Place ID.
ALTERNATIVSTED_ADRESSE_SQL = """SELECT [HusnrAltern],
                                     [ForbrStVejnavn],
                                     [VejkodeAltern],
                                     [Postdistrikt],
                                     [Postnr],
                                     [Bogstav],
                                     [EtageAltAdr],
                                     [SidedørnrAltern]
                            FROM AlternativSted
                            WHERE AlternativStedID = {0}
                          """
