<p><h3>Depot Überblick</h3></p>
<table border="1">
    <tr>
        <td><b>ISIN</b></td>
        <td><b>Papiername</b></td>
        <td><b>Stück</b></td>
        <td><b>Einstiegskurs</b></td>
        <td><b>Gesamtwert</b></td>
        <td><b>Devidende</b></td>
        <td><b>Gebühren</b></td>
    </tr>
    %for row in list:
    <tr>
      <td>{{row.isin}}</td>
      <td></td>
      <td>{{row.stueck}}</td>
      <td>{{row.kurs}}</td>
      <td>{{row.stueck * row.kurs}}
      <td>_</td>
      <td>_</td>
    </tr>
    %end
</table>