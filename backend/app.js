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

  app.get('/props/', (req, res) => {

    const QUERY = `
      SELECT 
        p.id,
        p.title,
        p.body,
        p.motion_id as motionId,
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
    `;
    const P_QUERY = mysql.format(QUERY, 1);
    con.query({
      sql: P_QUERY
    }, (err, props) => {
      let orderedProp = {};
      props.forEach((prop) => {
        const { motionId } = prop;
        if(!orderedProp[motionId]) { // if the prop doesnt exist
          const { id, title, body, yrkanden } = prop;
          orderedProp[motionId] = { id, title, body, motionId, yrkanden, senders: [] };
        }
        const { partyId, party, politicianId, politician } = prop;
        orderedProp[motionId].senders.push({ 
          partyId, 
          politicianId, 
          party, 
          politician 
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
