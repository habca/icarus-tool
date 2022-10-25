import assert = require("assert");
import { Koira } from "../src/helloworld";

describe("Hauku function", () => {
  it("should return name property", () => {
    const koira = new Koira("musti");
    assert.equal("musti", koira.hauku());
  });
});
