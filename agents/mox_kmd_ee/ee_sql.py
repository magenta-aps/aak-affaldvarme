#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""This module contains all SQL used in the KMD EE Mox Agent."""

# This is the SQL to fetch all customers from the KMD EE database.
# Only relevant fields (please).

CUSTOMER_SQL = """
SELECT top(100)  [PersonnrSEnr]
      ,[KundeCprnr]
      ,[LigestPersonnr]
      ,[Tilflytningsdato]
      ,[Fraflytningsdato]
      ,[EmailKunde]
      ,[MobilTlf]
      ,[KundeID]
      ,[Kundenr]
      ,[Status]
      ,[Telefonnr]
      ,[FasadministratorID]
      ,[BoligadminID]
      ,[KundeNavn]
      ,[ForbrugsstedID]
      ,[VejNavn]
      ,[Postdistrikt]
  FROM [KMD_EE].[dbo].[Kunde]
  WHERE Tilflytningsdato <= GETDATE() AND Fraflytningsdato >= GETDATE()
"""


TREFINSTALLATION_SQL = """SELECT *
    FROM TrefInstallation a, TrefMaaler b
    WHERE ForbrugsstedID = {0}
    AND a.InstallationID = b.InstallationID
    AND b.DatoFra <= GETDATE() and b.DatoTil >= GETDATE()
    """
FORBRUGSSTED_ADRESSE_SQL = """SELECT [Husnr],
                                     [ForbrStVejnavn],
                                     [Postdistrikt],
                                     [Postnr],
                                     [Bogstav],
                                     [Etage],
                                     [Sidedørnr]
                            FROM Forbrugssted
                            WHERE ForbrugsstedID = {0}
                            """
