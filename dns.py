#Copyright 2011 Matthew J. Smith (matt@forsetti.com)
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

from struct import pack,unpack

TYPES=["", "A", "NS", "", "", "CNAME",]
CLASSES=["", "IN",]


class LabelTooLong(Exception):
	pass

class NameTooLong(Exception):
	pass

class Name(bytearray):		
	def __decode__(self):
		i=0
		name=""
		while(self[i]):
			next=i+self[i]+1
			name+=self[i+1:next].decode()+"."
			i=next
		self.__name__=name

	@property
	def name(self):
		if(not hasattr(self,__name__)):
			self.__decode__()
		return(self.__name__)

	def __str__(self):
		return(self.name)
	
class StringName(Name):
	def __init__(self,name, encoding="ascii"):
		if(name[-1]!="."):
			name+="."
		
		self.__name__=name
		labels=name.split(".")
		t=bytearray(0)
		
		for label in labels:
			l=len(label)
			if(l>64): raise LabelTooLong(label)
			t+=bytes([len(label)])+label.encode()
			if(len(self)>255): raise NameTooLong(name)
		super().__init__(t)
	
class __ResourceRecord__(bytearray):
	def __init__(self, name, rr_type, rr_class, rr_ttl, rr_rdlength, rr_rdata):
		self.name=StringName(name)
		self.rr_type=rr_type
		self.rr_class=rr_class
		self.rr_ttl=rr_ttl
		self.rr_rdlength=rr_rdlength
		self.rr_rdata=rr_rdata
		
		super().__init__(self.name+pack("!HHLH",rr_type,rr_class,rr_ttl,rr_rdlength)+rr_rdata)
	
	def __str__(self):
		return("%s %s %s %s"%(self.name,TYPES[self.rr_type],CLASSES[self.rr_class],self.rr_ttl))
		
		
class CNameRR(__ResourceRecord__):
	def __init__(self, name, ttl, cname):
		self.cname=StringName(cname)
		super().__init__(name, 5, 1, ttl, len(self.cname), self.cname)

	def __str__(self):
		return(super().__str__()+" "+str(self.cname))

class NSRR(__ResourceRecord__):
	def __init__(self, name, ttl, nsdname):
		self.nsdname=StringName(nsdname)
		super().__init__(name, 2, 1, ttl, len(self.nsdname), self.nsdname)

	def __str__(self):
		return(super().__str__()+" "+str(self.nsdname))

class Question(bytes):
		
	def __str__(self):
		return("%s %s %s"%(self.qname,TYPES[self.qtype],CLASSES[self.qclass]))

	def __decode__(self):
		(self.__qtype__,self.__qclass__)=unpack("!HH",self[-4:])
		self.__qname__=Name(self[:-4])
		
	@property
	def qname(self):
		if(not hasattr(self,"__qname__")):
			self.__decode__()
		return(self.__qname__)
	
	@property
	def qtype(self):
		if(not hasattr(self,"__qtype__")):
			self.__decode__()
		return(self.__qtype__)	
	
	@property
	def qclass(self):
		if(not hasattr(self,"__qclass__")):
			self.__decode__()
		return(self.__qclass__)
		
class ComponentQuestion(Question):
	def __init__(self, qname, qtype, qclass=1):
		super().__init__(Name(qname)+pack("!HH",qtype,qclass))
		self.qname=qname
		self.qtype=qtype
		self.qclass=qclass
	
class Message(bytearray):
	
	@property
	def id(self):
		return(unpack("!H",self[0:2])[0])
	
	@property
	def qr(self):
		return(self[2]&0x80)
		
	@property
	def opcode(self):
		return((self[2]&0x78)>>3)
		
	@property
	def aa(self):
		return(self[2]&0x04)
		
	@property
	def tc(self):
		return(self[2]&0x02)
		
	@property
	def rd(self):
		return(self[2]&0x01)
	
	@property
	def ra(self):
		return(self[3]&0x80)
		
	@property
	def z(self):
		return((self[3]&0x70)>>4)
		
	@property
	def rcode(self):
		return(self[3]&0x0F)
		
	@property
	def qdcount(self):
		return(unpack("!H",self[4:6])[0])
		
	@property
	def ancount(self):
		return(unpack("!H",self[6:8])[0])
		
	@property
	def nscount(self):
		return(unpack("!H",self[8:10])[0])	
		
	@property
	def arcount(self):
		return(unpack("!H",self[10:12])[0])
		
	@property
	def questions(self):
		q1=12
		q2=q1
		for qdcount in range(self.qdcount):
			while(self[q2]):
				q2+=self[q2]+1
			q2+=4
			
			yield(Question(self[q1:q2+1]))
			q1=q2
			
	def __str__(self):
		return("ID:%s OPCODE:%s RCODE:%s "%(self.id,self.opcode,self.rcode)+("qr " if self.qr else "")+("aa " if self.aa else "")+("tc " if self.tc else "")+("rd " if self.rd else "")+("ra " if self.ra else "")+"QUERY:%s ANSWER:%s AUTHORITY:%s ADDITIONAL:%s"%(self.qdcount,self.ancount,self.nscount,self.arcount)+" "+" ".join([str(question) for question in self.questions]))
	
class Query(Message):
	pass
	
class Response(Message):		
	def __init__(self,query, answers=[], authorities=[], additionals=[]):
		pass
		#flags=bytes(2)
		#flags[2]=(opcode<<3)&78
		#if(qr): flags[2]|=0x80
		#if(aa): flags[2]|=0x04
		#if(tc): flags[2]|=0x02
		#if(rd): flags[2]|=0x01
		
		#flags[3]=rcode&0x0F
		#if(ra): flags[3]|=0x80
		#if(z): raise InvalidParameter("Z reserved for future use")
		
		#self.header=pack("!HHHHHH",id,flags,len(question),len(answer),len(authority),len(additional))
		##self.question=[question for question in questions]
