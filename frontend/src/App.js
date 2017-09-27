import React, { Component } from 'react';
import './App.css';
import axios from 'axios';

const UP = 'UP';
const DOWN = 'DOWN';
const NEXT = 'NEXT';
const PREV = 'PREV';

class App extends Component {

  constructor() {
    super();
    this.state = {
      page: 0,
      sorting: undefined,
      filter: undefined
    }
  }

  handlePageNav(type) {
    return (e) => {
      const { page } = this.state; 
      this.setState({
        page: (type === NEXT) ? page+1 : page-1
      });
    }
  }

  render() {

    const { page } = this.state;

    return (
      <div className="App">
        <button onClick={ this.handlePageNav(PREV).bind(this) }>⬅️</button>
        <span>{ page }</span>
        <button onClick={this.handlePageNav(NEXT).bind(this) }>➡️</button>
        <PropList {...this.state} />
      </div>
    );
  }
}

class PropList extends Component {

  constructor(props) {
    super();
    this.state = {
      propos: []
    };
  }

  componentWillReceiveProps({ page }) {
    if(page !== this.props.page) {
      this.setState({
        propos: []
      }, () => {
        this.fetchPropos(page);
      });
    }
  }

  componentWillMount() {
    this.fetchPropos(this.props.page);
  }

  fetchPropos(page) {
    const { hostname } = document.location;
    axios.get(`http://${hostname}:4000/props/${page}`).then((res) => {
      const propos = Object.keys(res.data).map(key => res.data[key]); // transform to array
      this.setState({
        propos: propos
      })
    });
  }

  render() {

    const listNode = (this.state.propos.length > 0) ? 
                      this.state.propos.map((propo) => 
                        <PropListItem key={ propo.id } { ...propo } />
                      ) :
                      <h1>Loading...</h1>;

    return (
      <ul>
        { listNode }
      </ul>
    );
  }
}

class PropListItem extends Component {

  constructor({ score }) {
    super();
    this.state = {
      score: score
    };
  }
  
  handleVote(type) {
    return (e) => {
      const { id } = this.props;
      const { hostname } = document.location;
      
      axios.post(`http://${hostname}:4000/props/${id}`, {
        action: 'vote',
        value: type
      }).then((res) => {
        const { success } = res.data;
        if(success === true) {
          const { score } = this.state;
          this.setState({
            score: (type === UP) ? score+1 : score-1
          });
        } else {
          console.error('Request failed.');
        }
      });
    }
  }

  getParties() {
    let parties = new Set();
    this.props.senders.forEach((sender) => {
      parties.add(sender.party);
    });
    return Array.from(parties);
  }

  render() {

    console.log(this.getParties());

    const { score } = this.state;
    const { title, url, motionId, body } = this.props;
    const blockStyle = { display: "block" };

    const flagNode = this.getParties().map((party) => {
      return <img className="partyFlag" src={`./images/logos/${party}.jpg`}/>
    });

    const cssClasses = this.getParties().map((party) => {
      return `party-${party}`;
    }).join(' ');

    return (
      <li className={`propo-item ${cssClasses}`}>
        <div className="info">
          <a href={ url } target="_blank">
            <p>{ title } : { motionId } </p>
          </a>
          <p className="body">{ body }</p>
        </div>
        <div className="voting">
          <button name="up" onClick={ this.handleVote(UP).bind(this) } style={blockStyle}>⬆️</button>
          <p>{ score } 🏆</p>
          <button name="down" onClick={ this.handleVote(DOWN).bind(this) } style={blockStyle}>⬇️</button>
        </div>
        <div className="flagContainer">
          { flagNode }
        </div>
      </li>
    )
  }
}

export default App;
