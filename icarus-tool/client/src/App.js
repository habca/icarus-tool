import { useState } from "react";
import "./styles/styles.css";

// TODO: 1 fabricator + 1 fabricator => 3 fabricator
// TODO: 1 hunting_rifle + 1 hunting_rifle => 3 hunting_rifle

const App = () => {
  // Set data to data_items
  const data_items = ["fabricator", "food", "filth", "abra", "kadabra"];
  const data_object = [
    {
      name: "fabricator",
      amount: 1,
      station: "machining_bench",
      children: [
        {
          name: "aluminium_ingot",
          amount: 40,
          station: "concrete_furnace",
          children: [
            {
              name: "aluminium_ore",
              amount: 40,
              station: undefined,
              children: []
            }
          ]
        },
        {
          name: "electronics",
          amount: 30,
          station: "machining_bench",
          children: []
        }, 
        {
          name: "concrete_mix",
          amount: 30,
          station: "cement_mixer",
          children: []
        },
        {
          name: "carbon_fiber",
          amount: 8,
          station: "concrete_furnace",
          children: []
        }, 
        {
          name: "steel_screw",
          amount: 30,
          station: "machining_bench",
          children: []
        }
      ]
    }
  ];

  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);

  const onchange = (event) => {
    setSearch(event.target.value);
  };

  const moveSelectedRight = () => {
    // Confirm selected and move to list
    const options = document.getElementById("search_results").options;
    const results = options
      .filter(option => option.selected)
      .map(option => option.value);
    setResults(results);
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
        <ul id="results_list">
          {
            data_object.map(child => {
              return <TreeElement key={child.name} name={child.name} amount={child.amount} station={child.station} children={child.children}></TreeElement>
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
  const { name, amount, station, children } = props;
  return(
    <>
      <li>{amount} {name} [{station}]</li>
      <ul>
        {children.map(child => {
          // TODO: yliviivaus checkbox
          return <TreeElement key={child.name} name={child.name} amount={child.amount} station={child.station} children={child.children}></TreeElement>
        })}
      </ul>
    </>
  );
}

export default App;
