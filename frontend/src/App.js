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
    axios.get(`http://localhost:4000/props/${page}`).then((res) => {
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
      axios.post(`http://localhost:4000/props/${id}`, {
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
    return this.props.senders.map()
  }

  render() {

    const { score } = this.state;
    const { title, url } = this.props;

    return (
      <li>
        <a href={ url } target="_blank">
          <p>{ title }</p>
        </a>
        <button name="up" onClick={ this.handleVote(UP).bind(this) }>UP</button>
        <p>{ score } 🏆</p>
        <button name="down" onClick={ this.handleVote(DOWN).bind(this) }>DOWN</button>
      </li>
    )
  }
}

export default App;
