SELECT 
	p.id,
	p.title,
	p.body,
	p.motion_id,
	p.yrkanden,
	pi.id as partyId,
	pi.symbol as party,
	po.id as politicianId,
	po.name as politician
FROM proposition_senders as ps
INNER JOIN propositions as p
ON p.id = ps.proposition_id
LEFT OUTER JOIN politicians as po
ON po.id = ps.politician_id
INNER JOIN parties as pi
ON po.party_id = pi.id
ORDER BY p.motion_id DESC
LIMIT ?