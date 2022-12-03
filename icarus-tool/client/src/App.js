import { useState } from "react";
import "./App.css";
import json_object from "./data/data.json";


// TODO: 1 fabricator + 1 fabricator => 3 fabricator
// TODO: 1 hunting_rifle + 1 hunting_rifle => 3 hunting_rifle

const App = () => {
  // Set data to data_items
  const data_items = ["fabricator", "food", "filth", "abra", "kadabra"];

  const [search, setSearch] = useState("");
  const [jsonArray, setJsonArray] = useState( json_object);
  const [selectedArray, setSelectedArray] = useState([]);

  const onchange = (event) => {
    setSearch(event.target.value);
  };

  const moveSelectedRight = () => {
    // Confirm selected and move to list
    const options = document.getElementById("search_results").options;
    const results = options
      .filter(option => option.selected)
      .map(option => option.value);
    setJsonArray(results);
  };

  const removeSelected = () => {
    let newJsonArray = [ ...jsonArray ];
    newJsonArray = newJsonArray.filter(item => !selectedArray.includes(item.name));
    setJsonArray(newJsonArray);
  };

  return (
    <>
      <h1> Material calculator</h1>
      <h6>Project Gray v.0.0.0.1.1 pre-beta / PRODUCTION / patent pending / Copyright (c) 1992 by Ville Web Designs LLC. / All rights reserved </h6>
      <div id="search_container">
      <input type="text" onChange={onchange} value={search}></input>
      <select id="search_results" multiple="multiple">
        {data_items
          .filter(x => x.includes(search))
          .map(item => {
            return <option key={item} value={item}>{item}</option>
          })}
      </select>
      <button id="move_right" value=">>" onClick={moveSelectedRight}> {">>"} </button>
      </div>

      <div id="results_container">
        <button onClick={removeSelected}> X </button>
        <ul id="results_list">
          {
            jsonArray.map(item => {
              return (
              <TreeElement key={item.name} first={true} name={item.name} amount={item.amount} count={item.count} station={item.station} children={item.children} jsonArray={jsonArray} setJsonArray={setJsonArray} selectedArray={selectedArray} setSelectedArray={setSelectedArray} />
              )
              // TODO: poista/muokkaa itemin määriä
            })
          }
        </ul>


      </div>
      
      <div id="totals_container">
          <h2> Total resources </h2>
      </div>
    </>
  );
}



const TreeElement = (props) => {
  const { name, first, amount, count, station, children, jsonArray, setJsonArray, selectedArray, setSelectedArray } = props;

  const increase = (name) => (event) => {
    let copy = [ ...jsonArray ];
    copy = copy.map(item => {
      if (item.name === name) {
        const oldValue = 1;
        const multiplier = event.target.value;
        const newValue = oldValue * multiplier;
        
        multiply(item.children, oldValue, newValue);
        item.amount = newValue;
      }
      return item;
    });
    setJsonArray(copy);
  }

  const multiply = (children, parentOldValue, parentNewValue) => {
    children.forEach(item => {
      const oldValue = item.amount;
      if (!item.multiplier) {
        item.multiplier = oldValue / parentOldValue;
      }
      const multiplier = item.multiplier;

      const newValue = parentNewValue * multiplier;

      multiply(item.children, oldValue, newValue);
      item.amount = newValue;
    });
  }

  const selectItem = (name) => (event) => {
    const newSelectedArray = [ ...selectedArray ];
    if (event.target.value === "ON") {
      event.target.value = "OFF";
      newSelectedArray.remove(name);
    } else {
      event.target.value = "ON";
      newSelectedArray.push(name);
    };
    setSelectedArray(newSelectedArray);
  }

  return(
    <>
        {first ? 
          <>
          <li>
            <button onClick={selectItem(name)} value="OFF">
            {amount} {name} [{station}]
            </button>
            <input onChange={increase(name)} type="number" min={0} max={10000} step={count} value={amount}></input>
            </li>
            
          </>
          : 
          <>
            <li>
            {amount} {name} [{station}]
            </li>
          </>
        }
        
      <ul>
        {children.map(child => {
          // TODO: yliviivaus checkbox
          return <TreeElement key={child.name} first={false} name={child.name} amount={child.amount} station={child.station} children={child.children}></TreeElement>
        })}
      </ul>
    </>
  );
}

export default App;
