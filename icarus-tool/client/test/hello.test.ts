import assert = require('assert');
import hello from '../src/hello';

describe('Hello function', () => {
    it('should return hello world', () => {
        const result = hello();
        assert.equal(result, 'Hello World!');
    });
});
