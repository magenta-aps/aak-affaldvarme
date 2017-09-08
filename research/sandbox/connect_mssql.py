# encoding: utf-8
# import pyodbc

import pymssql

SQL_EXAMPLE = """
SELECT TOP (10) [ForbrugsstedID]
      ,[StopAcontoTilOgMed]
      ,[AdresFormKunde]
      ,[LigestAdresseForm]
      ,[Afregningskode]
      ,[PersonnrSEnr]
      ,[LigestPersonnr]
      ,[Tilflytningsdato]
      ,[Fraflytningsdato]
      ,[EmailKunde]
      ,[FaxNr]
      ,[MobilTlf]
      ,[KundeID]
      ,[Kundenr]
      ,[Opkrævningsform]
      ,[Redigeringsnr]
      ,[SendesTil]
      ,[Regningstekst]
      ,[SidsteAfregnDato]
      ,[Status]
      ,[StopAfregning]
      ,[Telefonnr]
      ,[Velkomstbrev]
      ,[KundeAflKortSend]
      ,[BetalingAdvisdato]
      ,[AntalAcontorater]
      ,[AfregningsgrpNr]
      ,[FasadministratorID]
      ,[BoligadminID]
      ,[KundeWebStatus]
      ,[Rykkerstatus]
      ,[HenlagtTil]
      ,[Adviskode]
      ,[Advisdato]
      ,[Advistekst]
      ,[AntalMdrDepositum]
      ,[DepositumReg]
      ,[AntalMdrForudbLeje]
      ,[ForudbLejeReg]
      ,[BoligStøtteForm]
      ,[HuslejeTilBos]
      ,[UndertrykRegnUdskr]
      ,[LigestAltAdresseID]
      ,[KundeLokationsnr]
      ,[Kontoplannr]
      ,[Kontoplantekst]
      ,[PbsAftale]
      ,[PbsOplAftalenr]
      ,[PbsOplIkraftDato]
      ,[PbsOplTilmeldDato]
      ,[PbsOplAfmeldDato]
      ,[EBoksNummer]
      ,[KundeCprNr]
      ,[AdmvaerkID]
      ,[WebProfilID]
      ,[RedigFormID]
      ,[KundeSendForbOpl]
      ,[KundeUdbetForm]
      ,[KundeFasAdmNiveau]
      ,[KundeVelkomstDato]
      ,[KundeBankReg]
      ,[Bankkonto]
      ,[KundeCPRVData]
      ,[KundeCPRVDataLige]
      ,[KundeIdent]
      ,[KundePID]
      ,[KundeAntBoern]
      ,[KundeAntUnge]
      ,[KundeAntVoksne]
      ,[KundeChTime]
      ,[AntalAconto]
      ,[ReklameBeskyt]
      ,[BetalBetNavn]
      ,[KundeOIOordre]
      ,[KundeOIOkontakt]
      ,[KundeOIOkonto]
      ,[KundeSagsnr]
      ,[KortTlmCardExpMon]
      ,[KortTlmCardExpYear]
      ,[KortTlmDatoFra]
      ,[KortTlmDatoTil]
      ,[KortTlmStatus]
      ,[KundeEksternNr]
      ,[KundeNavn]
      ,[CONavn]
      ,[VejNavn]
      ,[ByNavn]
      ,[Postdistrikt]
      ,[TilmeldtEboksFak]
      ,[TilmeldtEboksAfl]
      ,[TilmeldtMailFak]
      ,[TilmeldtMailAfl]
  FROM [KMD_EE].[dbo].[Kunde]
"""

# ASCII/Unicode helper function

def enc(val):
    if type(val) == unicode:
        return val
    else:
        return unicode(val)


def connect(server, database, username, password):
    driver1= '{SQL Server}'
    driver2= '{ODBC Driver 13 for SQL Server}'
    print "Attempting connect..."
    #PORT=1433
    cnxn = None
    try:
        #cnxn = pyodbc.connect('DRIVER=' + driver1 + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        #cnxn = pyodbc.connect('DRIVER='+driver1+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
        #cnxn = pyodbc.connect(driver=driver1, server=server, database=database, username=username, password=password)
        cnxn = pymssql.connect(server=server, user=username, password=password, database=database)
    except Exception as e:
        print e
        raise
        return
    print "Connected"
    cursor = cnxn.cursor()
    cursor.execute(SQL_EXAMPLE)
    # cursor.execute("""select * from Forbrug
    #                  WHERE ForbrugsstedID=16456742""")
    row = cursor.fetchone()
    while row:
        # print str(row[0]) + " " + str(row[1]) + " " + str(row[2])
        print u" ".join(map(enc, row))
        row = cursor.fetchone()
    """
    cursor.execute("SELECT name from master.dbo.sysdatabases")
    row = cursor.fetchone()
    while row:
        # print str(row[0]) + " " + str(row[1]) + " " + str(row[2])
        print u" ".join(map(unicode, row))
        row = cursor.fetchone()
    """

if __name__ == '__main__':
    from mssql_config import username, password, server, database
    connect(server, database, username, password)
