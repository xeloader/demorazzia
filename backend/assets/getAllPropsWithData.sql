      SELECT 
        p.id,
        p.title,
        p.body,
        p.motion_id as motionId,
        p.yrkanden,
        pi.id as partyId,
        pi.symbol as party,
        po.id as politicianId,
        po.name as politician,
        (
          SELECT 
            SUM(IF(pv.vote = 'UP', 1, -1)) 
          FROM 
            proposition_votes as pv 
          WHERE 
            pv.proposition_id = p.id
        ) as score
      FROM proposition_senders as ps
      INNER JOIN propositions as p
      ON p.id = ps.proposition_id
      LEFT OUTER JOIN politicians as po
      ON po.id = ps.politician_id
      INNER JOIN parties as pi
      ON po.party_id = pi.id
      LEFT OUTER JOIN proposition_votes as pv
      ON pv.proposition_id = p.id
      ORDER BY p.motion_id DESC
      -- ORDER BY score DESC
      LIMIT ?