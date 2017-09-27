"""This module contains all SQL used in the KMD EE Mox Agent."""

# This is the SQL to fetch all customers from the KMD EE database.
# Only relevant fields (please).

CUSTOMER_SQL = """
SELECT [PersonnrSEnr]
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
  FROM [KMD_EE].[dbo].[Kunde]
  WHERE Tilflytningsdato <= GETDATE() AND Fraflytningsdato >= GETDATE()
"""


TREFINSTALLATION_SQL = """SELECT *
    FROM TrefInstallation a, TrefMaaler b
    WHERE ForbrugsstedID = {0}
    AND a.InstallationID = b.InstallationID
    AND b.DatoFra <= GETDATE() and b.DatoTil >= GETDATE()
    """
