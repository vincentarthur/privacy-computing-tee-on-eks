import logo from './logo.svg';
import './App.css';
import React from 'react';

import {Route, BrowserRouter} from 'react-router-dom';
import {Switch} from 'react-router';

import BreastCancerClassification from './pages/BreastCancerClassification'

function App() {
  return (
        <BrowserRouter>
            <Switch>
                <Route exact path="/" component={BreastCancerClassification}/>
                <Route exact path="/breast_cancer_classification" component={BreastCancerClassification}/>
            </Switch>
        </BrowserRouter>
    );
}

export default App;
