SELECT c.*, k.fileId, k.count,  m.countF
FROM mixcer_out.cdr3 c
left join mixcer_out.keystone_summary as k on k.aaCDR3 =  c.aaCDR3
left join (
	SELECT ID, aaSeqCDR3, sum(readCount) as countF 
	FROM mixcer_out.my_mixcr2
	WHERE aaSeqCDR3 NOT LIKE '%\_%' and aaSeqCDR3 NOT LIKE '%*%' and LENGTH(aaSeqCDR3) > 10
	GROUP BY ID, aaSeqCDR3
) as m on c.aaCDR3 = m.aaSeqCDR3 AND k.fileId = m.ID;

select sum(count) from mixcer_out.keystone_summary as k where k.fileId like '%OVA12-201229%';

select count(*) from mixcer_out.my_mixcr as m where m.ID like '%OVA12-201229%' and aaSeqCDR3 NOT LIKE '%\_%' and aaSeqCDR3 NOT LIKE '%*%' and LENGTH(aaSeqCDR3) > 10;

select * from mixcer_out.my_mixcr as m where 
	m.ID = "OVA3-201229_S3_L001"  and m.aaSeqCDR3 NOT LIKE '%\_%' and m.aaSeqCDR3 NOT LIKE '%*%' and LENGTH(m.aaSeqCDR3) > 10;
    
select aaSeqCDR3, count(*) from mixcer_out.my_mixcr2 as m where 	m.ID = "OVA3-201229_S3_L001" group by aaSeqCDR3 ;

select * from mixcer_out.my_mixcr2 as m where m.ID = "OVA3-201229_S3_L001" and aaSeqCDR3 = 'CAWTYGSKSWGTEAFF';

SELECT sum( m.countF)
FROM mixcer_out.cdr3 c
left join (
	SELECT aaSeqCDR3, count(aaSeqCDR3) as countF 
	FROM mixcer_out.my_mixcr2
	WHERE ID like '%OVA3-201229%' AND aaSeqCDR3 NOT LIKE '%\_%' and aaSeqCDR3 NOT LIKE '%*%' and LENGTH(aaSeqCDR3) > 10
	GROUP BY aaSeqCDR3
) as m on c.aaCDR3 = m.aaSeqCDR3;






SELECT SUM(countF) FROM (
SELECT c.*, k.fileId, k.count,  m.countF
FROM mixcer_out.cdr3 c
left join mixcer_out.keystone_summary as k on k.aaCDR3 =  c.aaCDR3
left join (
	SELECT ID, aaSeqCDR3, count(aaSeqCDR3) as countF 
	FROM mixcer_out.my_mixcr2
	WHERE ID = "OVA3-201229_S3_L001" AND aaSeqCDR3 NOT LIKE '%\_%' and aaSeqCDR3 NOT LIKE '%*%' and LENGTH(aaSeqCDR3) > 10
	GROUP BY ID, aaSeqCDR3
) as m on c.aaCDR3 = m.aaSeqCDR3 AND k.fileId = m.ID) as t1