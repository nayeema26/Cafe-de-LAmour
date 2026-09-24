function confirmDelete(what){return confirm("Are you sure you want to delete " + what + "?");}

function initOrderCalculator(){
  const rows = document.querySelectorAll(".order-row");
  const totalEl = document.getElementById("order-total");
  function recalc(){
    let total=0;
    rows.forEach(row=>{
      const check=row.querySelector(".item-check");
      const qty=row.querySelector(".qty");
      const line=row.querySelector(".line-total");
      const price=parseFloat(qty.dataset.price||0);
      const n=parseInt(qty.value||0);
      const lineTotal=check.checked && n>0 ? price*n : 0;
      line.textContent="₹"+lineTotal.toFixed(2);
      total+=lineTotal;
    });
    totalEl.textContent="₹"+total.toFixed(2);
  }
  document.querySelectorAll(".item-check,.qty").forEach(el=>el.addEventListener("input",recalc));
  document.querySelectorAll(".item-check").forEach(el=>el.addEventListener("change",recalc));
  recalc();
}
