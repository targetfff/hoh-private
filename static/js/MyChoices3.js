
    var elements = document.querySelectorAll('.options_for_select');
    var lst = [{value: 0, label: 'Без родителя',
                description: 'Категория будет считаться одной из "основных"'}];
    elements.forEach(el => {
        Option = {value: $(el).attr('id'), label: $(el).val()};
        lst.push(Option);
    });
        VirtualSelect.init({
  ele: '#example-select',
  hasOptionDescription: true,
  options: lst,
  search: true,
  name: 'parent',
  placeholder: 'Выберите нового родителя',
  multiple: false,
  optionsCount: 4,
  optionHeight: '60%',
  required: true,
  maxWidth: '100%',
  noOptionsText: 'Пока что категорий нет...',
  noSearchResultsText: 'Ничего не найдено',
  searchPlaceholderText: 'Поиск...',
});


    var elements2 = document.querySelectorAll('.options_for_select2');
    var lst2 = [];
    elements2.forEach(el => {
        Option = {value: $(el).attr('id'), label: $(el).val()};
        lst2.push(Option);
    });
        VirtualSelect.init({
  ele: '#example-select2',
  hasOptionDescription: true,
  options: lst2,
  search: true,
  name: 'this',
  placeholder: 'Выберите категорию для изменения',
  multiple: false,
  optionsCount: 4,
  optionHeight: '60%',
  required: true,
  maxWidth: '100%',
  noOptionsText: 'Пока что категорий нет...',
  noSearchResultsText: 'Ничего не найдено',
  searchPlaceholderText: 'Поиск...',
});