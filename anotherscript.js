let treesParameters = {akacja: 0.85, brzoza: 0.9, dab: 1.2, jesion: 1.1, jodla: 1.08, klon: 1.15, orzech: 1.25, sosna: 1.0, topola: 1.05, swierk: 0.95, inne: 1.00};
let species = document.getElementById('species2');
let output = document.getElementById('output');
let size = document.getElementById('num');
let size2 = document.getElementById('num2');
function calculate()
{
    if(size.value == 0 || size2.value == 0)
    {
        alert("prosimy uzupełnić wszystkie pola");
        return 0;
    }

    if(species.value === "none")
    {
        alert("prosimy wybrać gatunek drzewa");
        return 0;
    }
    let r = Number(size.value) / 2 * Math.PI;
    output.innerHTML = `Obliczone wchłanianie CO<sup>2</sup> : ${(treesParameters[species.value] * ((Math.PI * (r * r) * Number(size2.value)) / 1000000)).toFixed(2)}kg`;
};