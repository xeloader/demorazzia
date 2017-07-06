SELECT 
	pi.symbol,
	COUNT(p.title) as n_props
FROM proposition_senders as ps
INNER JOIN propositions as p
ON p.id = ps.proposition_id
LEFT OUTER JOIN politicians as po
ON po.id = ps.politician_id
INNER JOIN parties as pi
ON po.party_id = pi.id
GROUP BY pi.symbol
ORDER BY n_props