import { Injectable } from '@angular/core';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

@Injectable({
  providedIn: 'root'
})
export class PdfService {

  public gerarPDF(elementId: string, nomeArquivo: string) {
    const data = document.getElementById(elementId);

    if (data) {
      // Adicionamos 'backgroundColor: null' para evitar problemas com transparências
      html2canvas(data, {
        scale: 2,
        backgroundColor: '#ffffff', // Força fundo branco (evita oklch transparente)
        useCORS: true // Ajuda se houver imagens externas
      }).then(canvas => {
        const imgWidth = 208;
        const pageHeight = 295;
        const imgHeight = canvas.height * imgWidth / canvas.width;

        const contentDataURL = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');

        pdf.addImage(contentDataURL, 'PNG', 0, 0, imgWidth, imgHeight);
        pdf.save(`${nomeArquivo}.pdf`);
      }).catch(err => {
        console.error("Erro ao gerar PDF:", err);
        alert("Erro ao gerar PDF. Tente usar um navegador moderno (Chrome/Edge).");
      });
    }
  }
}
