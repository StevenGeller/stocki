__author__ = 'steven'

import csv
import os
from datetime import datetime
import re
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pprint import pprint
from sqlalchemy import update
from bottle import route, run, template,view


db = create_engine('sqlite://data/db')
db.echo = False
Base = declarative_base()
Base.metadata.bind = db
Session = sessionmaker(bind=db)


class Stock(Base):
    __tablename__ = 'stock'
    isin = Column(String(250), nullable=False, primary_key=True)
    papiername = Column(String(250), nullable=False)


class Depot(Base):
    __tablename__ = 'depot'
    isin = Column(String(250), primary_key=True, nullable=False)
    kurs = Column(Float, nullable=False)
    stueck = Column(Integer, nullable=False)


class Account(Base):
    __tablename__ = 'account'
    transactionNr = Column(Integer, nullable=False, primary_key=True)
    isin = Column(String(250), ForeignKey('stock.isin'))
    forAccountTransactions = Column(Integer)
    forAccountTransactions = Column(Integer)
    buchungstag = Column(Date, primary_key=True)
    valutatag = Column(Date, primary_key=True)
    addInformation = Column(String(250))
    betrag = Column(Float)


class Transaction(Base):
    __tablename__ = 'transaction'
    transactionNr = Column(Integer, nullable=False, primary_key=True)
    buchungstag = Column(Date, primary_key=True)
    valutatag = Column(Date, primary_key=True)
    isin = Column(String(250), ForeignKey('stock.isin'))
    stueck = Column(Integer)
    addInformation = Column(String(250))
    kurs = Column(Float)

Base.metadata.create_all(db)


def read_all_csv_depot():

    path = r'data/depot'
    session = Session()

    for file in os.listdir(path):
        if file.endswith(".csv"):
            csvfile = open(path + '/' + file, 'rb')
            creader = csv.reader(csvfile, delimiter=';', quotechar='|')
            creader.next()
            for t in creader:
                parsedBuchungsinfo = str(t[7]).split('TA.-Nr.')

                # TODO: Suche aktie zuerst - moment exception
                try:
                    stock = Stock(isin=t[3] , papiername=t[4])
                    session.add(stock)
                    transactionNr = int(str(parsedBuchungsinfo[1]).replace('TA.-Nr. ', ''))

                    transaction = Transaction(transactionNr= transactionNr,
                                              buchungstag=datetime.strptime(t[1], "%d.%m.%Y").date(),
                                              valutatag=datetime.strptime(t[2], "%d.%m.%Y").date(),
                                              stueck=float(str(t[5]).replace('.','').replace(',','.')),
                                              addInformation=parsedBuchungsinfo[0].decode('unicode-escape'),
                                              kurs=float(str(t[8]).replace('.','').replace(',','.')),
                                              isin=stock.isin
                                              )
                    session.add(transaction)
                    session.commit()
                except Exception, e:
                    session.rollback()


                # TODO: Suche transaction zuerst - moment exception
                try:
                    transactionNr = int(str(parsedBuchungsinfo[1]).replace('TA.-Nr. ', ''))

                    transaction = Transaction(transactionNr= transactionNr,
                                              buchungstag=datetime.strptime(t[1], "%d.%m.%Y").date(),
                                              valutatag=datetime.strptime(t[2], "%d.%m.%Y").date(),
                                              stueck=float(str(t[5]).replace('.','').replace(',','.')),
                                              addInformation=parsedBuchungsinfo[0].decode('unicode-escape'),
                                              kurs=float(str(t[8]).replace('.','').replace(',','.')),
                                              isin=stock.isin
                                              )
                    session.add(transaction)
                    session.commit()
                except Exception, e:
                    session.rollback()

            csvfile.close()
    session.close()


def reset_depot():
    session = Session()
    q = session.query(Stock).all()
    for stock in q:
        n = session.query(Depot).filter_by(isin=stock.isin).all()
        if len(n) == 0:
            m = session.query(Transaction).filter_by(isin=stock.isin).all()

            for transaction in m:
                computeDepotTransaction(stock, transaction)

    session.close


def computeDepotTransaction(stock, transaction):
    session = Session()

    existingDepotItem = session.query(Depot).filter_by(isin=stock.isin).first()

    if existingDepotItem is not None:
        if (existingDepotItem.stueck + transaction.stueck) > 0:
            p1 = existingDepotItem.stueck * existingDepotItem.kurs
            p2 = transaction.stueck * transaction.kurs
            newPrice = (p1 + p2) / (existingDepotItem.stueck + transaction.stueck)
            existingDepotItem.stueck += transaction.stueck
            existingDepotItem.kurs = newPrice
            try:
                session.add(existingDepotItem)
                session.commit()
            except Exception, e:
                print e

        else:
            session.delete(existingDepotItem)
            session.commit()

    else:
         if (transaction.stueck) > 0:
             depot = Depot(isin=stock.isin, kurs=transaction.kurs, stueck=transaction.stueck)
             session.add(depot)
             session.commit()

    session.close()


def initial_by_depot_csv():
    csvfile = open('data/Depotbestand.csv', 'rb')
    creader = csv.reader(csvfile, delimiter=';', quotechar='|')
    session = Session()

    creader.next()
    for t in creader:
        if len(session.query(Depot).filter_by(isin=t[1]).all()) == 0:

            try:
                depot = Depot(isin= t[1],
                              kurs=float(str(t[4]).replace(' EUR', '').replace('.','').replace(',','.')),
                              stueck=int(float(str(t[3]).replace(' Stk.', '').replace('.','').replace(',','.')))
                              )
                session.add(depot)
                if session.query(Stock).filter_by(isin=t[1]).all() is None:
                    stock = Stock(isin=t[1], papiername=t[0])
                    session.add(stock)

                session.commit()
            except Exception, e:
                print e
                session.rollback()
    csvfile.close()
    session.close()


def read_all_cvs_account():
    path = r'data/konto'
    session = Session()

    for file in os.listdir(path):
        if file.endswith(".csv"):
            csvfile = open(path + '/' + file, 'rb')
            creader = csv.reader(csvfile, delimiter=';', quotechar='|')

            creader.next()
            for t in creader:
                parsedBuchungsinfo = str(t[4]).split(':')
                a = parsedBuchungsinfo[0]
                m = re.search('[A-Z]{2}[0-9]+[A-Z0-9]*',str(parsedBuchungsinfo))
                try:
                    isin = m.group(0)

                except:
                    isin = None
                try:
                    account = Account(
                        buchungstag=datetime.strptime(t[0], "%d.%m.%Y").date(),
                        valutatag=datetime.strptime(t[1], "%d.%m.%Y").date(),
                        betrag=float(str(t[5]).replace('.','').replace(',','.')),
                        isin=isin,
                        transactionNr=parsedBuchungsinfo[1],
                        addInformation=t[4].decode('unicode-escape')
                    )
                    session.add(account)
                    session.commit()
                except Exception, e:
                    session.rollback()

            csvfile.close()
    session.close()


def get_depot_balance():
    session = Session()
    total = 0
    depot = session.query(Depot).all()
    for h in depot:
        total += h.stueck * h.kurs

    return total


def get_all_depot_items():
    session = Session()
    depot = session.query(Depot).all()
    return depot


def get_all_transactions(isin):
    session = Session()
    searchtransaction = session.query(Transaction).filter(Transaction.isin == isin)
    return searchtransaction


def compute_totalgainloses(list):
    total = 0
    for k in list.values():
        total = total + k

    return total


def list_gainsloses_year(year):
    session = Session()
    totalgainloses = {}
    startyear = str(year) + '-01-01'
    endyear = str(year+1) + '-01-01'
    alltransactions = session.query(Transaction).filter(and_(Transaction.buchungstag <= endyear,
                                                 Transaction.buchungstag >= startyear
    ))

    for t in alltransactions:
        if t.stueck < 0:
            totalgainloses[t.isin] = 0
            transactions = session.query(Transaction).filter(Transaction.isin == t.isin)
            for t2 in transactions:
                if t2.stueck > 0:
                    totalgainloses[t.isin] = totalgainloses[t.isin] - (abs(t2.stueck) * t2.kurs)

                else:
                    totalgainloses[t.isin] = totalgainloses[t.isin] + (abs(t2.stueck) * t2.kurs)

    return totalgainloses


def get_all_gainsloses():
    session = Session()
    totalgainloses = {}
    alltransactions = session.query(Transaction).all()
    for t in alltransactions:
        if t.stueck < 0:
            totalgainloses[t.isin] = 0
            transactions = session.query(Transaction).filter(Transaction.isin == t.isin)
            for t2 in transactions:
                if t2.stueck > 0:
                    totalgainloses[t.isin] = totalgainloses[t.isin] - (abs(t2.stueck) * t2.kurs)

                else:
                    totalgainloses[t.isin] = totalgainloses[t.isin] + (abs(t2.stueck) * t2.kurs)
    return totalgainloses


def initilizeProgram():
    read_all_csv_depot()
    reset_depot()
    read_all_cvs_account()
    initial_by_depot_csv()
    print(get_all_gainsloses)
    # print compute_totalgainloses(get_all_gainsloses)

initilizeProgram()

#@route('/')
#@view('table_template')
#def index():
#    session = Session()
#    output = template("table_template", list=session.query(Depot).all())
#    return output
#run(host='localhost', port=8080)

