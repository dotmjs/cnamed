#!/usr/bin/python3
import dns

#id=28424
query=dns.Query(list(b'o\x08\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x04mail\x07example\x03org\x00\x00\x01\x00\x01'))
for question in query.questions:
	print(question)
print(query)
#cname=dns.CNameRR("mail.example.com",86400,"foobar.localhost.org")
#ns1=dns.NSRR("example.com",300,"ns1.example.com")
#ns2=dns.NSRR("example.com",300,"ns2.example.com")
#print(cname)
#print(ns1)
#print(ns2)
#print(bytes(cname))
#print(bytes(ns1))
#print(bytes(ns2))

#n1=dns.StringName("this.example.com")
#n2=dns.Name(b'\x05this2\x07example\x03com\x00')
#print(n1)
#print(n2)
#print(bytes(n1))
#print(bytes(n2))
