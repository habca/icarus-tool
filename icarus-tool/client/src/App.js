import { useState } from "react";
import "./App.css";
import TreeElement from "./components/TreeElement";
import json_object from "./data/data.json";

const App = () => {
  // Set data to data_items
  const data_items = ["fabricator", "food", "filth", "abra", "kadabra"];

  const [search, setSearch] = useState("");
  const [jsonArray, setJsonArray] = useState(json_object);
  const [selectedArray, setSelectedArray] = useState([]);
  const [styleArray, setStyleArray] = useState([]);

  const onchange = (event) => {
    setSearch(event.target.value);
  };

  const moveSelectedRight = () => {
    // Confirm selected and move to list
    /*
    const options = document.getElementById("search_results");
    const results = options
      .filter((option) => option.selected)
      .map((option) => option.value);
    setJsonArray(results);
    */
  };

  /**
   * Removes the selected items from the tree view.
   * Removes the selection afterwards.
   */
  const removeSelected = () => {
    let newJsonArray = [...jsonArray];
    newJsonArray = newJsonArray.filter(
      (item) => !selectedArray.includes(item.name)
    );

    let newStyleArray = [...styleArray];
    newStyleArray = newStyleArray.filter(
      (name) => !selectedArray.includes(name)
    );

    setJsonArray(newJsonArray);
    setStyleArray(newStyleArray);
    setSelectedArray([]);
  };

  /**
   * Toggles between states show or hide.
   * Removes the selection afterwards.
   */
  const acquireItem = () => {
    let newStyleArray = [...styleArray];
    selectedArray.forEach((itemName) => {
      if (newStyleArray.includes(itemName)) {
        newStyleArray = newStyleArray.filter((name) => name !== itemName);
      } else {
        newStyleArray = newStyleArray.concat(itemName);
      }
    });
    setStyleArray(newStyleArray);
    setSelectedArray([]);
  };

  const selectAllItems = () => {
    if (selectedArray.length < jsonArray.length) {
      setSelectedArray(jsonArray.map((item) => item.name));
    } else {
      setSelectedArray([]);
    }
  };

  const getSelectionStatus = () => {
    const count = selectedArray.length;
    return count > 0 ? count + " selected item(s)" : null;
  };

  return (
    <>
      <h1> Material calculator</h1>
      <h6>
        Project Gray v.0.0.0.1.1 pre-beta / PRODUCTION / patent pending /
        Copyright (c) 1992 by Ville Web Designs LLC. / All rights reserved{" "}
      </h6>
      <div id="search_container">
        <input
          type="text"
          onChange={onchange}
          placeholder="search"
          value={search}
        ></input>
        <select id="search_results" multiple="multiple">
          {data_items
            .filter((x) => x.includes(search))
            .map((item, index) => {
              return (
                <option key={"search" + item + index} value={item}>
                  {item}
                </option>
              );
            })}
        </select>
        <button id="move_right" value=">>" onClick={moveSelectedRight}>
          {" "}
          {">>"}{" "}
        </button>
      </div>

      <div id="results_container">
        <button onClick={acquireItem}> Done </button>
        <button onClick={selectAllItems}> All </button>
        <button onClick={removeSelected}> Delete </button>
        {getSelectionStatus()}
        <ul id="results_list">
          {jsonArray.map((item, index) => {
            return (
              <TreeElement
                key={item.name + "layer" + 1 + "index" + index}
                layer={1}
                first={true}
                name={item.name}
                amount={item.amount}
                count={item.count}
                station={item.station}
                children={item.children}
                jsonArray={jsonArray}
                setJsonArray={setJsonArray}
                selectedArray={selectedArray}
                setSelectedArray={setSelectedArray}
                crossout={styleArray.includes(item.name)}
              />
            );
          })}
        </ul>
      </div>

      <div id="totals_container">
        <h2> Total resources </h2>
      </div>
    </>
  );
};

export default App;
