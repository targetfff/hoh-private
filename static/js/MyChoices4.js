    const elements = document.querySelectorAll('.options_for_select');
    var lst = [];
    elements.forEach(el => {
        Option = {value: $(el).attr('id'), label: $(el).val()};
        lst.push(Option);
    });
    console.log(lst)
    if (lst.length > 0) {
        VirtualSelect.init({
  ele: '#example-select',
  hasOptionDescription: false,
  options: lst,
  search: true,
  name: 'vendor',
  placeholder: 'Выберите продавца',
  multiple: false,
  optionsCount: 4,
  optionHeight: '40%',
  hideClearButton: true,
  required: true,
  maxWidth: '80%',
  selectedValue: lst[0]['value'],
  dropboxWidth: '100%',
  noOptionsText: 'Для данного товара пока нет продавцов',
  noSearchResultsText: 'Ничего не найдено',
  searchPlaceholderText: 'Поиск...',
});} else {
    VirtualSelect.init({
        ele: '#example-select',
        hasOptionDescription: false,
        options: lst,
        search: true,
        name: 'vendor',
        placeholder: 'Выберите продавца',
        multiple: false,
        optionsCount: 4,
        optionHeight: '40%',
        hideClearButton: true,
        required: true,
        maxWidth: '80%',
        dropboxWidth: '100%',
        noOptionsText: 'Для данного товара пока нет продавцов',
        noSearchResultsText: 'Ничего не найдено',
        searchPlaceholderText: 'Поиск...',
      });
}