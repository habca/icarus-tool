
export class Koira {
    private nimi: string;
    constructor(nimi: string) {
        this.nimi = nimi;
    }
    public hauku(): string {
        return this.nimi;
    }
}

const musti = new Koira("Teppo");
console.log(musti.hauku())
