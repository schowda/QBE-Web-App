import sys
import re
import graphene
import mysql.connector as mysql

def flatten_dict(dd, separator ='/', prefix =''):
    return { prefix + separator + k if prefix else k : v
             for kk, vv in dd.items()
             for k, v in flatten_dict(vv, separator, kk).items()
             } if isinstance(dd, dict) else { prefix : dd }
class Tables(graphene.ObjectType):
    tablename = graphene.String()

class TableAttributes(graphene.ObjectType):
    attributeName = graphene.String()

class QueryResults(graphene.ObjectType):
    recValue = graphene.List(graphene.String)
    querystr = graphene.String()

class Queries(graphene.ObjectType):
    alltables = graphene.List(Tables,username=graphene.String(), password=graphene.String(), dbname=graphene.String())
    tableAttributes = graphene.List(TableAttributes,tablename=graphene.String(), username=graphene.String(), password=graphene.String(), dbname=graphene.String())
    Qres=graphene.List(QueryResults,username=graphene.String(), password=graphene.String(), dbname=graphene.String(),sTables=graphene.String(),Columns=graphene.String(),conditionBox=graphene.String())
    #def resolve_all_tables(self, info, username=graphene.String(), password=graphene.String(), dbname=graphene.String()):

    def resolve_alltables(self, info, username, password, dbname):
        db = mysql.connect(
            host="localhost",
            database=dbname,
            user=username,
            passwd=password,
            auth_plugin='mysql_native_password'
        )
        query = "show tables"
        cursor = db.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        db.close()
        #if len(records) == 0:
        #  return ??
        alltables = []
        for record in records:
            alltables.append(Tables(tablename=record[0]))
        return alltables

    def resolve_tableAttributes(self, info, tablename, username, password, dbname):
        db = mysql.connect(
            host="localhost",
            database=dbname,
            user=username,
            passwd=password,
            auth_plugin='mysql_native_password'
        )
        query = "desc "+tablename
        cursor = db.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        db.close()
        #if len(records) == 0:
        #  return ??
        tableAttributes = []
        tableAttributes.append(TableAttributes(attributeName=tablename))
        for record in records:
            tableAttributes.append(TableAttributes(attributeName=record[0]))
        return tableAttributes

    def resolve_Qres(self, info, username, password, dbname, sTables, Columns, conditionBox):
        db = mysql.connect(
            host="localhost",
            database=dbname,
            user=username,
            passwd=password,
            auth_plugin='mysql_native_password'
        )

        #VARIABLES DECLARATION and ASSIGNMENT --------------------
        tot={}
        selectedTables = sTables.split(",")
        selectedColumns = Columns.split(",")
        dupselectedColumns=selectedColumns
        actualTables = []
        for temp in selectedTables:
            temp2=temp.split("_",1)
            actualTables.append(temp2[0])
        for temp in selectedTables:
            col={}
            actualColumns = []
            temp2=temp.split("_",1)[0]
            query = "desc "+temp2
            cursor = db.cursor()
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            actualColumns.append(temp)
            for record in records:
                actualColumns.append(record[0])
            for i in range(len(actualColumns)):
                col[actualColumns[i]]=dupselectedColumns[0]
                dupselectedColumns.pop(0)
            tot[temp]=col
        #print(selectedTables)
        print(selectedColumns)
        #print(actualTables)
        #print(actualColumns)
        #i=0
        """for j in range(len(actualTables)):
            while(actualColumns[i]!=actualTables[j])
                col[actualColumns[i]]=selectedColumns[i]
            tot[selectedTables[j]]=col"""
        print(tot)

        #SQL QUERY----------------------------------------------------------------

        #select----------------
        query="select "
        for table_name in selectedTables:
            actTable=table_name.split("_",1)[0]
            flag=0
            count=0
            c=tot[table_name]
            for column_name in c:
                if(flag==0):
                    if(c[column_name]=="P." and count==0):
                        flag=1;
                    elif((re.match(r"P\.",c[column_name]) or re.match(r"P\._.*",c[column_name])) and count!=0):
                        query=query+table_name+"."+column_name+" AS "+table_name+"_"+column_name+","
                else:
                    query=query+table_name+"."+column_name+" AS "+table_name+"_"+column_name+","
                count=count+1
        query=query[:-1]+" from "
        for table_name in selectedTables:
            tempTable=table_name.split("_",1)[0]
            query=query+tempTable+" "+table_name+","
        query=query[:-1]

        #join-----------------------
        flag=0
        pp=flatten_dict(tot)
        flipped = {}
        for key, value in pp.items():
            trek=value.replace('P.','')
            print(trek)
            if trek not in flipped:
                flipped[trek] = [key]
            else:
                flipped[trek].append(key)
        print(flipped)
        flag=0
        count=0
        for dots in flipped:
            if(dots!="P." and dots!="NULL" and dots!='' and len(flipped[dots])>1):
                join_columns=flipped[dots]
                flag=flag+1
                count=count+1;
            if(flag==1):
                if(count==1):
                    query=query+" where "
                elif(count>1):
                    query=query+" and "
                init=join_columns[0].replace("/",".")
                p=len(join_columns)
                for i in range(1,p):
                    tempString=join_columns[i].replace("/",".")
                    print(i,p)
                    if(i!=p-1):
                        query=query+init+"="+tempString+" and "
                    else:
                        query=query+init+"="+tempString
                flag=0


        #Condition--------------------------
        order=[]
        for dots in flipped:
            if(re.match(r"P\._.*",dots) or (re.match(r"_.*",dots) and len(flipped[dots])==1)):
                query=query+" and "
                match=re.findall('_.*',dots)[0]
                str=''
                str=str.join(flipped[dots][0])
                str=str.replace("/",".")
                conditionBox=conditionBox.replace(match,str)
                query=query+conditionBox
            elif(re.match(r"'.*'",dots)):
                query=query+" and "
                match2=re.findall('\'.*\'',dots)[0]
                str2=''
                str2=str2.join(flipped[dots])
                str2=str2.replace("/",".")
                query=query+str2+"="+match2
            elif(re.match(r"AO(.)",dots)):
                match3=re.findall('\(.\)',dots)[0]
                match3=match3[1:]
                match3=match3[:-1]
                str3=''
                str3=str3.join(flipped[dots])
                str3=str3.replace("/",".")
                order.append([str3,'AO',int(match3)])
            elif(re.match(r"DO(.)",dots)):
                match4=re.findall('\(.\)',dots)[0]
                match4=match4[1:]
                match4=match4[:-1]
                str4=''
                str4=str4.join(flipped[dots])
                str4=str4.replace("/",".")
                order.append([str4,'DO',int(match4)])

        #Order by-------------------------------------
        if(len(order)!=0):
            query=query+" order by "
            order.sort(key=lambda x:x[2])
            for elements in order:
                if(elements[1]=='AO'):
                    query=query+elements[0]+" ASC,"
                elif(elements[1]=='DO'):
                    query=query+elements[0]+" DESC,"
            query=query[:-1]

        #Run Query-----------------------------------------------------------------
        print(query)
        cursor = db.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        bokka=cursor.column_names
        bokka2=[]
        cursor.close()
        Qres=[]
        for values in bokka:
                bokka2.append(values)
        Qres.append(QueryResults(recValue=bokka2,querystr=query))
        for record in records:
            Qres.append(QueryResults(recValue=record,querystr="NULL"))
        return Qres
        """query = "desc "+tablename
        cursor = db.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        db.close()
        #if len(records) == 0:
        #  return ??
        tableAttributes = []
        tableAttributes.append(TableAttributes(attributeName=tablename))
        for record in records:
            tableAttributes.append(TableAttributes(attributeName=record[0]))
        return tableAttributes"""
        db.close()
schema = graphene.Schema(query=Queries)
