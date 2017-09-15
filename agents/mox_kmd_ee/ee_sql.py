"""This module contains all SQL used in the KMD EE Mox Agent."""

# This is the SQL to fetch all customers from the KMD EE database.
# Only relevant fields (please).

CUSTOMER_SQL = """
SELECT TOP(10) [PersonnrSEnr]
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
  FROM [KMD_EE].[dbo].[Kunde]
"""
