import express from 'express';
import bodyParser from 'body-parser';
import mysql from 'mysql';
import 'source-map-support/register';

const app = express();

const ENV = process.env.NODE_ENV ? process.env.NODE_ENV.toUpperCase() : 'DEV';
const PORT = ENV === 'TEST' ? 4001 : 4000;

const con = mysql.createConnection({
  host: '127.0.0.1',
  user: 'root',
  password: 'root',
  database: 'demorazzia',
  port: 8889
});

  app.use(bodyParser.json({ type: '*/*' })); // matches every filetype to JSON
  app.use(bodyParser.urlencoded({ extended: true }));

  app.post('/props/:id', (req, res) => {
    console.log(req.params, req.body);
    if(req.body.action) {
      const action = req.body.action.toLowerCase();
      switch(action) {
        case "vote":
          if(req.body.value) {
            const vote = req.body.value;
            const propId = req.params.id;
            const QUERY = `
              INSERT INTO proposition_votes
              (proposition_id, vote)
              VALUES
              (?, ?)
            `;
            const P_QUERY = mysql.format(QUERY, [propId, vote])
            con.query({
              sql: P_QUERY
            }, (err, result) => {
              res.json({ success: !err, data: { vote, propId } });
              console.log(result);
              
            });
          }
        break;
      }
    } else {
      res.status(401).send('Fuck off boring asshole');
    }
  })

  app.get('/props/:p', (req, res) => {

    const QUERY = `
      SELECT 
        p.id,
        p.title,
        p.body,
        p.motion_id as motionId,
        p.yrkanden,
        p.pdf_url as pdfUrl,
        p.url,
        pi.id as partyId,
        pi.symbol as party,
        po.id as politicianId,
        po.name as politician,
        po.picture_url as pictureUrl,
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
      LIMIT ?, ?
    `;

    const PER_PAGE = 25;
    const start = parseInt(req.params.p) * PER_PAGE;
    console.log(start, PER_PAGE); 

    const P_QUERY = mysql.format(QUERY, [start, PER_PAGE]);
    con.query({
      sql: P_QUERY
    }, (err, props) => {
      let orderedProp = {};
      props.forEach((prop) => {
        const { motionId } = prop;
        if(!orderedProp[motionId]) { // if the prop doesnt exist
          const { id, title, body, yrkanden, score, pdfUrl, url } = prop;
          orderedProp[motionId] = { id, title, score, body, motionId, yrkanden, senders: [] };
        }
        const { partyId, party, politicianId, politician, pictureUrl } = prop;
        orderedProp[motionId].senders.push({ 
          partyId, 
          politicianId, 
          party, 
          politician,
          pictureUrl
        });
      })
      res.json(orderedProp);
    });

  });

  con.connect((err) => {
    console.log(`[${ENV}] Database Connected`);
    if(!err) {
      app.listen(PORT, () => {
        console.log(`[${ENV}] Demorazzia is fucking shit up at port ${PORT}.`);
      });
    } else {
      console.log(`[${ENV}] Something went wrong with the DB connection`)
    }

  });
