const TreeElement = (props) => {
  const {
    name,
    layer,
    first,
    amount,
    count,
    station,
    children,
    jsonArray,
    setJsonArray,
    selectedArray,
    setSelectedArray,
    crossout,
  } = props;

  const increase = (name) => (event) => {
    let copy = [...jsonArray];
    copy = copy.map((item) => {
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
  };

  const multiply = (children, parentOldValue, parentNewValue) => {
    children.forEach((item) => {
      const oldValue = item.amount;
      if (!item.multiplier) {
        item.multiplier = oldValue / parentOldValue;
      }
      const multiplier = item.multiplier;

      const newValue = parentNewValue * multiplier;

      multiply(item.children, oldValue, newValue);
      item.amount = newValue;
    });
  };

  const selectItem = (itemName) => (event) => {
    let newSelectedArray = [...selectedArray];
    if (newSelectedArray.includes(itemName)) {
      newSelectedArray = newSelectedArray.filter((name) => name !== itemName);
    } else {
      newSelectedArray = newSelectedArray.concat(itemName);
    }
    setSelectedArray(newSelectedArray);
  };

  const toggleSelected = (name) => {
    return selectedArray.includes(name) ? "ON" : "OFF";
  };

  const toggleCrossout = (crossout) => {
    return crossout ? "CROSSOUT" : "NORMAL";
  };

  const newLayer = layer + 1;

  if (first) {
    return (
      <>
        <li>
          <button
            onClick={selectItem(name)}
            value={toggleSelected(name)}
            className={toggleCrossout(crossout)}
          >
            {amount} {name} [{station}]
          </button>
          <input
            onChange={increase(name)}
            type="number"
            min={0}
            max={10000}
            step={count}
            value={amount}
          ></input>
        </li>

        {!crossout ? (
          <ul>
            {children.map((child, index) => {
              return (
                <TreeElement
                  key={child.name + "layer" + newLayer + "index" + index}
                  layer={newLayer}
                  first={false}
                  name={child.name}
                  amount={child.amount}
                  station={child.station}
                  children={child.children}
                  crossout={crossout}
                ></TreeElement>
              );
            })}
          </ul>
        ) : (
          <></>
        )}
      </>
    );
  }

  return (
    <>
      <li>
        {amount} {name} [{station}]
      </li>

      <ul>
        {children.map((child, index) => {
          return (
            <TreeElement
              key={child.name + "layer" + newLayer + "index" + index}
              layer={newLayer}
              first={false}
              name={child.name}
              amount={child.amount}
              station={child.station}
              children={child.children}
              crossout={crossout}
            ></TreeElement>
          );
        })}
      </ul>
    </>
  );
};

export default TreeElement;
