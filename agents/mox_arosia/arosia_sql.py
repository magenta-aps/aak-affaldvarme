CONTACT_SQL = """
SELECT 
        [ava_CPRnummer],
        [ava_CVRnummer],
        [MobilePhone], 
        [Telephone1],
        [EMailAddress1],
        [ava_sms_notifikation],
        [ContactId],
        [ava_pnummer]
    FROM [arhafadm_MSCRM].[dbo].[Contact]
"""

ACCOUNT_SQL = """
SELECT
        [Name],
        [AccountNumber],
        [ava_Kundeforholdstype], 
        [AccountId]
    FROM [arhafadm_MSCRM].[dbo].[Account]
"""

KONTAKTROLLE_SQL = """
SELECT 
        [ava_Kontakt],
        [ava_KontaktName],
        [ava_Kundeforhold],
        [ava_Rolle] 
    FROM [arhafadm_MSCRM].[dbo].[ava_kontaktrolle]
    WHERE [ava_Kundeforhold] IS NOT NULL
"""

KUNDEAFTALE_SQL = """
SELECT top(100) 
        [ava_navn],
        [ava_kundeforhold],
        [ava_Kundeforholdname],
        [ava_Startdato], 
        [ava_Slutdato], 
        [ava_kundeaftaleId] 
    FROM [arhafadm_MSCRM].[dbo].[ava_kundeaftale]
"""

PLACERETMATERIEL_SQL = """
SELECT top(100) 
        [ava_navn],
        [ava_stregkode],
        [ava_Kundeaftale], 
        [ava_affaldstypename], 
        [ava_placeretmaterielId] 
    FROM [arhafadm_MSCRM].[dbo].[ava_placeretmateriel]
"""

CONTACT_SQL_RECENT = """
SELECT top(100) 
        [ava_CPRnummer],
        [ava_CVRnummer],
        [MobilePhone], 
        [Telephone1],
        [EMailAddress1],
        [ava_sms_notifikation],
        [ContactId],
        [ava_pnummer]
    FROM [arhafadm_MSCRM].[dbo].[Contact]
    WHERE ModifiedOn >= DATEADD(DAY, -1, GETDATE())
"""

ACCOUNT_SQL_RECENT = """
SELECT top(100) 
        [Name],
        [AccountNumber],
        [ava_Kundeforholdstype], 
        [AccountId]
    FROM [arhafadm_MSCRM].[dbo].[Account]
    WHERE ModifiedOn >= DATEADD(DAY, -1, GETDATE())
"""

KONTAKTROLLE_SQL_RECENT = """
SELECT top(100) 
        [ava_Kontakt],
        [ava_KontaktName],
        [ava_Kundeforhold],
        [ava_Rolle] 
    FROM [arhafadm_MSCRM].[dbo].[ava_kontaktrolle]
    WHERE [ava_Kundeforhold] IS NOT NULL
    AND ModifiedOn >= DATEADD(DAY, -1, GETDATE())
"""

KUNDEAFTALE_SQL_RECENT = """
SELECT top(100) 
        [ava_navn],
        [ava_kundeforhold],
        [ava_KundeforholdName],
        [ava_Startdato], 
        [ava_Slutdato], 
        [ava_kundeaftaleId] 
    FROM [arhafadm_MSCRM].[dbo].[ava_kundeaftale]
    WHERE ModifiedOn >= DATEADD(DAY, -1, GETDATE())
"""

PLACERETMATERIEL_SQL_RECENT = """
SELECT top(100) 
        [ava_navn],
        [ava_stregkode],
        [ava_Kundeaftale], 
        [ava_affaldstypeName], 
        [ava_placeretmaterielId] 
    FROM [arhafadm_MSCRM].[dbo].[ava_placeretmateriel]
    WHERE ModifiedOn >= DATEADD(DAY, -1, GETDATE())
"""
